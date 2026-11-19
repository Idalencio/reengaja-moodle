"""Confere as leituras da API em um Moodle configurado, sem enviar e-mails."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from acompanhamento.moodle import MoodleClient
from acompanhamento.service import eligible
from infra.config import Settings


def verify(settings):
    client = MoodleClient(settings)
    checks = []

    def read(name, function):
        start = time.monotonic()
        result = function()
        checks.append({"function": name, "passed": True,
                       "duration_seconds": round(time.monotonic() - start, 3)})
        return result

    assignments = read("mod_assign_get_assignments", client.assignments)
    visible = read("core_course_get_contents", client.visible_modules)
    students = read("core_enrol_get_enrolled_users", client.students)
    submissions = {}
    for task in assignments:
        identifier = int(task["id"])
        records = read("mod_assign_get_submissions", lambda: client.submissions(identifier))
        submissions[str(identifier)] = len(records)
    now = int(time.time())
    return {
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "moodle_url": settings.moodle_url,
        "course_id": settings.course_id,
        "checks": checks,
        "assignment_count": len(assignments),
        "visible_assignment_modules": len(visible),
        "active_student_count": len(students),
        "submission_counts": submissions,
        "eligible_assignment_ids": [int(a["id"]) for a in assignments
                                     if eligible(a, visible, now, settings.course_id)],
        "assignment_submission_read_verified": bool(assignments),
        "smtp_flow_verified": False,
        "note": "Leitura da API; não substitui os testes do fluxo até o SMTP. Sem tarefas, a leitura de entregas não é exercitada.",
    }


if __name__ == "__main__":
    result = verify(Settings.load())
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("evidencias/moodle_leituras.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
