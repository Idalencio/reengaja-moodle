"""Configuração por ambiente; nenhum segredo é escrito nos logs."""
from dataclasses import dataclass
import os
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


def secret(name, default=""):
    filename = os.getenv(name + "_FILE")
    return Path(filename).read_text().strip() if filename else os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    moodle_url: str = "http://moodle-demo:8080"
    moodle_token: str = "token-demonstracao"
    course_id: int = 42
    amqp_url: str = "amqp://reengaja:demo-local@rabbitmq:5672/%2F"
    queue_prefix: str = "reengajamento"
    interval: int = 3600
    http_timeout: int = 10
    http_attempts: int = 3
    retry_delay_ms: int = 60000
    max_attempts: int = 3
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_timeout: int = 10
    smtp_security: str = "none"
    smtp_user: str = ""
    smtp_password: str = ""
    mail_from: str = "Reengaja Moodle <lembretes@example.test>"
    timezone: str = "America/Sao_Paulo"
    database: str = "/data/notificacoes.sqlite3"
    health_port: int = 8081

    @classmethod
    def load(cls):
        return cls(
            moodle_url=os.getenv("MOODLE_URL", cls.moodle_url).rstrip("/"),
            moodle_token=secret("MOODLE_TOKEN", cls.moodle_token),
            course_id=int(os.getenv("MOODLE_COURSE_ID", cls.course_id)),
            amqp_url=secret("AMQP_URL", cls.amqp_url),
            queue_prefix=os.getenv("QUEUE_PREFIX", cls.queue_prefix),
            interval=int(os.getenv("POLL_INTERVAL_SECONDS", cls.interval)),
            http_timeout=int(os.getenv("HTTP_TIMEOUT_SECONDS", cls.http_timeout)),
            http_attempts=int(os.getenv("HTTP_ATTEMPTS", cls.http_attempts)),
            retry_delay_ms=int(os.getenv("RETRY_DELAY_MS", cls.retry_delay_ms)),
            max_attempts=int(os.getenv("MAX_ATTEMPTS", cls.max_attempts)),
            smtp_host=os.getenv("SMTP_HOST", cls.smtp_host),
            smtp_port=int(os.getenv("SMTP_PORT", cls.smtp_port)),
            smtp_timeout=int(os.getenv("SMTP_TIMEOUT_SECONDS", cls.smtp_timeout)),
            smtp_security=os.getenv("SMTP_SECURITY", cls.smtp_security),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=secret("SMTP_PASSWORD"),
            mail_from=os.getenv("MAIL_FROM", cls.mail_from),
            timezone=os.getenv("DISPLAY_TIMEZONE", cls.timezone),
            database=os.getenv("DATABASE_PATH", cls.database),
            health_port=int(os.getenv("HEALTH_PORT", cls.health_port)),
        ).validate()

    def validate(self):
        url = urlsplit(self.moodle_url)
        if url.scheme not in ("http", "https") or not url.hostname or url.query or url.fragment or url.username:
            raise ValueError("MOODLE_URL deve ser uma URL HTTP(S) base, sem credenciais ou parâmetros")
        if not self.moodle_token or self.course_id <= 0:
            raise ValueError("Token e ID positivo do curso são obrigatórios")
        for value in (self.interval, self.http_timeout, self.http_attempts, self.retry_delay_ms,
                      self.max_attempts, self.smtp_timeout, self.smtp_port, self.health_port):
            if value <= 0:
                raise ValueError("Intervalos, tentativas e portas devem ser positivos")
        if self.smtp_security not in ("none", "starttls", "ssl"):
            raise ValueError("SMTP_SECURITY: none, starttls ou ssl")
        if bool(self.smtp_user) != bool(self.smtp_password):
            raise ValueError("Configure SMTP_USER e SMTP_PASSWORD juntos")
        if self.smtp_user and self.smtp_security == "none":
            raise ValueError("Autenticação SMTP exige TLS")
        if not self.queue_prefix or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for c in self.queue_prefix):
            raise ValueError("QUEUE_PREFIX inválido")
        ZoneInfo(self.timezone)
        return self
