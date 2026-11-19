"""Adaptador Moodle REST; autenticação em POST e validação conservadora."""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class MoodleError(RuntimeError):
    pass


class MoodleClient:
    def __init__(self, settings, opener=urlopen, sleep=time.sleep):
        self.settings = settings
        self.opener = opener
        self.sleep = sleep

    def call(self, function, parameters):
        data = urlencode({"wstoken": self.settings.moodle_token, "wsfunction": function,
                          "moodlewsrestformat": "json", **parameters}).encode()
        request = Request(self.settings.moodle_url + "/webservice/rest/server.php", data=data,
                          headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        for attempt in range(self.settings.http_attempts):
            try:
                with self.opener(request, timeout=self.settings.http_timeout) as response:
                    result = json.load(response)
                if isinstance(result, dict):
                    if result.get("exception") or result.get("errorcode"):
                        raise MoodleError("Moodle rejeitou a operação " + function)
                    if result.get("warnings"):
                        raise MoodleError("Moodle retornou avisos; ciclo interrompido por segurança")
                return result
            except HTTPError as exc:
                if exc.code < 500 and exc.code != 429:
                    raise MoodleError(f"HTTP {exc.code} em {function}") from None
            except (URLError, TimeoutError, OSError):
                pass
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise MoodleError("Resposta JSON inválida em " + function) from None
            if attempt + 1 < self.settings.http_attempts:
                self.sleep(min(2 ** attempt, 8))
        raise MoodleError("Indisponibilidade HTTP em " + function)

    def assignments(self):
        result = self.call("mod_assign_get_assignments", {"courseids[0]": self.settings.course_id})
        if not isinstance(result, dict) or not isinstance(result.get("courses"), list):
            raise MoodleError("Lista de cursos ausente")
        courses = [c for c in result["courses"] if int(c["id"]) == self.settings.course_id]
        if len(courses) != 1 or not isinstance(courses[0].get("assignments"), list):
            raise MoodleError("Curso não retornado ou estrutura inválida")
        return courses[0]["assignments"]

    def visible_modules(self):
        result = self.call("core_course_get_contents", {"courseid": self.settings.course_id})
        if not isinstance(result, list):
            raise MoodleError("Conteúdo do curso inválido")
        visible = set()
        for section in result:
            if not section.get("visible", 0) or not section.get("uservisible", True) or section.get("availabilityinfo"):
                continue
            for module in section.get("modules", []):
                if (module.get("modname") == "assign" and module.get("visible", 0)
                        and module.get("uservisible", True) and module.get("visibleoncoursepage", 1)
                        and not module.get("availability") and not module.get("availabilityinfo")):
                    visible.add(int(module["id"]))
        return visible

    def students(self):
        students = {}
        offset = 0
        while True:
            options = [("withcapability", "mod/assign:submit"), ("onlyactive", "1"),
                       ("userfields", "id,fullname,email"), ("limitfrom", str(offset)),
                       ("limitnumber", "200"), ("sortby", "id"), ("sortdirection", "ASC")]
            parameters = {"courseid": self.settings.course_id}
            for i, (name, value) in enumerate(options):
                parameters[f"options[{i}][name]"] = name
                parameters[f"options[{i}][value]"] = value
            page = self.call("core_enrol_get_enrolled_users", parameters)
            if not isinstance(page, list):
                raise MoodleError("Lista de estudantes inválida")
            before = len(students)
            for student in page:
                students[int(student["id"])] = student
            if len(page) < 200:
                return list(students.values())
            if len(students) == before:
                raise MoodleError("Paginação sem progresso")
            offset += len(page)

    def submissions(self, assignment_id):
        result = self.call("mod_assign_get_submissions", {"assignmentids[0]": assignment_id})
        if not isinstance(result, dict) or not isinstance(result.get("assignments"), list):
            raise MoodleError("Lista de entregas ausente")
        assignments = [a for a in result["assignments"] if int(a["assignmentid"]) == assignment_id]
        if len(assignments) != 1 or not isinstance(assignments[0].get("submissions"), list):
            raise MoodleError("Tarefa não retornada na consulta de entregas")
        return assignments[0]["submissions"]
