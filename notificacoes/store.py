"""SQLite persistente. BEGIN IMMEDIATE serializa consumidores que compartilham o volume.

SMTP e SQLite não têm transação distribuída: consulte a limitação no README.
"""
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import smtplib
import time
from notificacoes.mailer import permanent_failure


@dataclass(frozen=True)
class Result:
    status: str
    attempts: int
    error_type: str = ""


class Store:
    def __init__(self, path):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS deliveries (
                    event_id TEXT PRIMARY KEY,
                    course_id INTEGER NOT NULL,
                    assignment_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    updated_at INTEGER NOT NULL,
                    error_type TEXT,
                    UNIQUE(course_id, assignment_id, student_id)
                );
                CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    attempts INTEGER NOT NULL,
                    error_type TEXT,
                    recorded_at INTEGER NOT NULL
                );
            """)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.execute("PRAGMA synchronous=FULL")
        return db

    def process(self, event, mailer, max_attempts=3, now=None):
        event.validate()
        now = int(time.time()) if now is None else now
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status, attempts, error_type FROM deliveries WHERE event_id=?", (event.event_id,)).fetchone()
            if row and row[0] in ("sent", "expired", "dead"):
                result = Result("duplicate" if row[0] == "sent" else row[0], row[1], row[2] or "")
            elif event.due_at <= now:
                result = Result("expired", row[1] if row else 0)
            else:
                attempts = (row[1] if row else 0) + 1
                if attempts > max_attempts:
                    result = Result("dead", attempts - 1, row[2] or "attempt_limit")
                else:
                    try:
                        mailer.send(event)
                        result = Result("sent", attempts)
                    except (OSError, smtplib.SMTPException) as exc:
                        result = Result("dead" if permanent_failure(exc) or attempts >= max_attempts else "retry",
                                        attempts, type(exc).__name__)
            if result.status != "duplicate":
                db.execute("""INSERT INTO deliveries VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                              ON CONFLICT(event_id) DO UPDATE SET status=excluded.status,
                              attempts=excluded.attempts, updated_at=excluded.updated_at,
                              error_type=excluded.error_type""",
                           (event.event_id, event.course_id, event.assignment_id, event.student_id,
                            result.status, result.attempts, now, result.error_type))
            db.execute("INSERT INTO audit(event_id,outcome,attempts,error_type,recorded_at) VALUES(?,?,?,?,?)",
                       (event.event_id, result.status, result.attempts, result.error_type, now))
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
