"""Regras do domínio e orquestração de um ciclo de acompanhamento."""
import html
import re
import time
from infra.events import Reminder
from infra.logging import log


def plain_text(value):
    return " ".join(html.unescape(re.sub(r"<[^>]*>", "", str(value))).split())


def eligible(assignment, visible_modules, now, course_id):
    return (int(assignment["course"]) == course_id
            and int(assignment["cmid"]) in visible_modules
            and not int(assignment.get("teamsubmission", 0))
            and not int(assignment.get("nosubmissions", 0))
            and not int(assignment.get("blindmarking", 0))
            and int(assignment.get("allowsubmissionsfromdate", 0)) <= now
            and (int(assignment.get("cutoffdate", 0)) == 0 or int(assignment["cutoffdate"]) > now)
            and 0 < int(assignment["duedate"]) - now <= 86400)


def submitted_users(submissions):
    # A API retorna a tentativa mais recente. A seleção também protege fixtures/variações antigas.
    latest = {}
    for submission in submissions:
        uid = int(submission["userid"])
        key = (int(submission.get("attemptnumber", 0)), int(submission.get("timemodified", 0)))
        if uid not in latest or key > latest[uid][0]:
            latest[uid] = (key, submission["status"])
    return {uid for uid, (_, status) in latest.items() if status == "submitted"}


def scan(moodle, settings, now=None):
    now = int(time.time()) if now is None else now
    assignments = moodle.assignments()
    visible = moodle.visible_modules()
    selected = [a for a in assignments if eligible(a, visible, now, settings.course_id)]
    if not selected:
        return []
    students = moodle.students()
    events = []
    for assignment in selected:
        submitted = submitted_users(moodle.submissions(int(assignment["id"])))
        for student in students:
            if int(student["id"]) in submitted:
                continue
            event = Reminder(
                course_id=settings.course_id, assignment_id=int(assignment["id"]), student_id=int(student["id"]),
                student_name=plain_text(student.get("fullname", "Estudante")),
                student_email=student.get("email", ""), assignment_name=plain_text(assignment["name"]),
                due_at=int(assignment["duedate"]),
                assignment_url=f"{settings.moodle_url}/mod/assign/view.php?id={assignment['cmid']}", created_at=now,
            )
            try:
                events.append(event.validate())
            except ValueError:
                log("estudante_ignorado", course_id=settings.course_id, assignment_id=assignment["id"],
                    student_id=student["id"], reason="dados_de_contato_invalidos")
    # Só publica depois de obter todas as respostas com sucesso.
    return events


def run_cycle(moodle, broker, settings, now=None):
    events = scan(moodle, settings, now)
    for event in events:
        broker.publish(event.encode(), event.event_id)
        log("solicitacao_publicada", event_id=event.event_id)
    log("ciclo_concluido", published=len(events))
    return events
