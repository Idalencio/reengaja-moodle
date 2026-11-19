"""Contrato v1. A chave de idempotência inclui curso, tarefa e estudante."""
from dataclasses import asdict, dataclass
import json
import re
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Reminder:
    course_id: int
    assignment_id: int
    student_id: int
    student_name: str
    student_email: str
    assignment_name: str
    due_at: int
    assignment_url: str
    created_at: int
    schema_version: int = 1

    @property
    def event_id(self):
        return f"{self.course_id}:{self.assignment_id}:{self.student_id}"

    def validate(self):
        for value in (self.course_id, self.assignment_id, self.student_id, self.due_at, self.created_at):
            if type(value) is not int or value <= 0:
                raise ValueError("Identificadores e instantes devem ser inteiros positivos")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("Versão de contrato não suportada")
        for value in (self.student_name, self.student_email, self.assignment_name, self.assignment_url):
            if not isinstance(value, str) or not value.strip() or len(value) > 2000 or any(c in value for c in "\r\n\x00"):
                raise ValueError("Campo de texto inválido")
        if not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", self.student_email):
            raise ValueError("E-mail ausente ou inválido")
        url = urlsplit(self.assignment_url)
        if url.scheme not in ("https", "http") or not url.hostname or url.username or url.password:
            raise ValueError("Link inválido")
        return self

    def encode(self):
        self.validate()
        return json.dumps({**asdict(self), "event_id": self.event_id}, ensure_ascii=False).encode()

    @classmethod
    def decode(cls, body):
        if len(body) > 32768:
            raise ValueError("Mensagem excede 32 KiB")
        try:
            values = json.loads(body)
            if not isinstance(values, dict):
                raise ValueError("Objeto JSON esperado")
            event_id = values.pop("event_id")
            event = cls(**values).validate()
            if event.event_id != event_id:
                raise ValueError("Chave de idempotência incompatível")
            return event
        except (KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("Contrato de mensagem inválido") from exc
