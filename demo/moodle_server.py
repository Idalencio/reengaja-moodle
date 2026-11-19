"""Simulador de contrato Moodle para demonstração. Não é uma instalação Moodle."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import time
from urllib.parse import parse_qs


def fixtures(now):
    def task(identifier, name, delta, **extra):
        return {"id": identifier, "cmid": identifier + 1000, "course": 42, "name": name,
                "duedate": now + delta if delta else 0, "allowsubmissionsfromdate": 0,
                "cutoffdate": 0, "teamsubmission": 0, "nosubmissions": 0,
                "blindmarking": 0, **extra}

    tasks = [task(501, "Projeto de Engenharia de Software II", 7200),
             task(502, "Atividade já vencida", -60), task(503, "Atividade para daqui a 48 horas", 172800),
             task(504, "Atividade sem prazo", 0), task(505, "Atividade em grupo", 7200, teamsubmission=1),
             task(506, "Atividade oculta", 7200), task(507, "Atividade ainda fechada", 7200, allowsubmissionsfromdate=now+3600),
             task(508, "Atividade restrita", 7200), task(509, "Atividade offline", 7200, nosubmissions=1)]
    modules = [{"id": t["cmid"], "modname": "assign", "visible": 0 if t["id"] == 506 else 1,
                "uservisible": True, "visibleoncoursepage": 1,
                **({"availability": '{"op":"&","c":[{"type":"group","id":7}]}'} if t["id"] == 508 else {})}
               for t in tasks]
    return {"tasks": tasks, "contents": [{"id": 1, "visible": 1, "uservisible": True, "modules": modules}],
            "students": [{"id": 101, "fullname": "Ana Exemplo", "email": "ana@example.test"},
                         {"id": 102, "fullname": "Bruno Exemplo", "email": "bruno@example.test"},
                         {"id": 103, "fullname": "Carla Exemplo", "email": "carla@example.test"}],
            "submissions": [{"userid": 102, "status": "submitted", "attemptnumber": 0, "timemodified": now-100},
                            {"userid": 103, "status": "draft", "attemptnumber": 0, "timemodified": now-50}]}


class Handler(BaseHTTPRequestHandler):
    def send_json(self, value, status=200):
        data = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.send_json({"status": "ok", "mode": "simulador"})
        elif self.path == "/fixture":
            self.send_json(self.server.data)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/webservice/rest/server.php":
            self.send_error(404)
            return
        size = int(self.headers.get("Content-Length", 0))
        if size > 65536:
            self.send_error(413)
            return
        params = {key: values[0] for key, values in parse_qs(self.rfile.read(size).decode()).items()}
        if params.get("wstoken") != "token-demonstracao":
            self.send_json({"exception": "moodle_exception", "errorcode": "invalidtoken"})
            return
        function = params.get("wsfunction")
        data = self.server.data
        if function == "mod_assign_get_assignments":
            self.send_json({"courses": [{"id": 42, "assignments": data["tasks"]}], "warnings": []})
        elif function == "core_course_get_contents":
            self.send_json(data["contents"])
        elif function == "core_enrol_get_enrolled_users":
            options = {params.get(f"options[{i}][name]"): params.get(f"options[{i}][value]") for i in range(7)}
            offset = int(options.get("limitfrom", 0))
            self.send_json(data["students"][offset:offset+200])
        elif function == "mod_assign_get_submissions":
            aid = int(params.get("assignmentids[0]", 0))
            self.send_json({"assignments": [{"assignmentid": aid,
                            "submissions": data["submissions"] if aid == 501 else []}], "warnings": []})
        else:
            self.send_json({"exception": "moodle_exception", "errorcode": "invalidfunction"})

    def log_message(self, *_):
        pass


def create_server(host="0.0.0.0", port=8080):
    server = ThreadingHTTPServer((host, port), Handler)
    server.data = fixtures(int(time.time()))
    return server


if __name__ == "__main__":
    print("Simulador Moodle REST: contas fictícias e prazo fixado ao iniciar", flush=True)
    create_server(port=int(os.getenv("DEMO_PORT", "8080"))).serve_forever()
