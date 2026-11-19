from dataclasses import asdict, replace
import json
import pytest
from infra.events import Reminder


def test_round_trip(event):
    assert Reminder.decode(event.encode()) == event
    assert event.event_id == "42:501:101"


@pytest.mark.parametrize("field,value", [("course_id", 0), ("assignment_id", -1), ("student_id", True),
                                       ("due_at", "123"), ("created_at", 0), ("schema_version", 2),
                                       ("schema_version", True), ("student_email", "sem-email"),
                                       ("student_email", "x@example.test\r\nBcc:outro@example.test"),
                                       ("student_name", ""), ("assignment_name", "a\nb"),
                                       ("assignment_name", "x" * 2001), ("assignment_url", "javascript:alert(1)"),
                                       ("assignment_url", "https://user:senha@example.test")])
def test_invalid_fields(event, field, value):
    with pytest.raises(ValueError):
        replace(event, **{field: value}).validate()


@pytest.mark.parametrize("body", [b"not json", b"[]", b"{}", b"\xff", b"x" * 32769])
def test_invalid_payload(body):
    with pytest.raises(ValueError):
        Reminder.decode(body)


def test_tampered_key(event):
    body = {**asdict(event), "event_id": "42:501:102"}
    with pytest.raises(ValueError):
        Reminder.decode(json.dumps(body).encode())


def test_unknown_field(event):
    body = json.loads(event.encode())
    body["injected"] = "field"
    with pytest.raises(ValueError):
        Reminder.decode(json.dumps(body).encode())
