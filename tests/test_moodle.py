from dataclasses import replace
from io import BytesIO
import json
from unittest.mock import Mock
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs
import pytest
from acompanhamento.moodle import MoodleClient, MoodleError


def response(value):
    return BytesIO(json.dumps(value).encode())


def test_post_and_secret_not_in_url(settings):
    opener = Mock(return_value=response({"courses": []}))
    client = MoodleClient(settings, opener)
    client.call("mod_assign_get_assignments", {"courseids[0]": 42})
    request = opener.call_args.args[0]
    assert request.get_method() == "POST"
    assert settings.moodle_token not in request.full_url
    assert parse_qs(request.data.decode())["courseids[0]"] == ["42"]


@pytest.mark.parametrize("error", [URLError("network"), TimeoutError(), HTTPError("url", 503, "down", {}, None)])
def test_transient_http_retry(settings, error):
    opener, sleep = Mock(side_effect=[error, response([])]), Mock()
    assert MoodleClient(settings, opener, sleep).call("test", {}) == []
    sleep.assert_called_once_with(1)


def test_http_retry_exhausted(settings):
    opener, sleep = Mock(side_effect=URLError("secret")), Mock()
    with pytest.raises(MoodleError, match="Indisponibilidade"):
        MoodleClient(settings, opener, sleep).call("test", {})
    assert opener.call_count == settings.http_attempts
    assert sleep.call_count == settings.http_attempts - 1


@pytest.mark.parametrize("payload", [{"exception": "error", "message": "secret"}, {"warnings": [{"message": "denied"}]}])
def test_moodle_partial_or_error_fails_closed(settings, payload):
    with pytest.raises(MoodleError):
        MoodleClient(settings, Mock(return_value=response(payload))).call("test", {})


def test_unauthorized_no_retry(settings):
    opener = Mock(side_effect=HTTPError("url", 403, "secret", {}, None))
    with pytest.raises(MoodleError, match="HTTP 403"):
        MoodleClient(settings, opener).call("test", {})
    assert opener.call_count == 1


def test_bad_json(settings):
    with pytest.raises(MoodleError, match="JSON inválida"):
        MoodleClient(settings, Mock(return_value=BytesIO(b"<html>error</html>"))).call("test", {})


def test_assignments_shape(settings):
    client = MoodleClient(settings)
    client.call = Mock(return_value={"courses": [{"id": 42, "assignments": [{"id": 1}]}]})
    assert client.assignments() == [{"id": 1}]


@pytest.mark.parametrize("payload", [{}, {"courses": []}, {"courses": [{"id": 99, "assignments": []}]}])
def test_missing_course_is_not_empty_success(settings, payload):
    client = MoodleClient(settings)
    client.call = Mock(return_value=payload)
    with pytest.raises(MoodleError):
        client.assignments()


def test_visibility(settings):
    client = MoodleClient(settings)
    client.call = Mock(return_value=[{"visible": 1, "modules": [
        {"id": 1, "modname": "assign", "visible": 1}, {"id": 2, "modname": "assign", "visible": 0},
        {"id": 3, "modname": "assign", "visible": 1, "availability": '{"op":"&"}'},
        {"id": 4, "modname": "assign", "visible": 1, "uservisible": False},
        {"id": 5, "modname": "assign", "visible": 1, "visibleoncoursepage": 0},
        {"id": 6, "modname": "quiz", "visible": 1},
    ]}, {"visible": 0, "modules": [{"id": 7, "modname": "assign", "visible": 1}]}])
    assert client.visible_modules() == {1}


def test_paginated_active_students(settings):
    client = MoodleClient(settings)
    client.call = Mock(side_effect=[[{"id": i} for i in range(1, 201)], [{"id": 201}]])
    assert len(client.students()) == 201
    params = client.call.call_args.args[1]
    assert params["options[3][value]"] == "200"
    assert params["options[0][value]"] == "mod/assign:submit"
    assert params["options[1][value]"] == "1"


def test_pagination_must_progress(settings):
    client = MoodleClient(settings)
    client.call = Mock(return_value=[{"id": i} for i in range(200)])
    with pytest.raises(MoodleError, match="Paginação"):
        client.students()


def test_submissions_shape(settings):
    client = MoodleClient(settings)
    client.call = Mock(return_value={"assignments": [{"assignmentid": 501, "submissions": []}]})
    assert client.submissions(501) == []


@pytest.mark.parametrize("payload", [{}, {"assignments": []}, {"assignments": [{"assignmentid": 999, "submissions": []}]}])
def test_incomplete_submissions_cannot_be_treated_as_no_delivery(settings, payload):
    client = MoodleClient(settings)
    client.call = Mock(return_value=payload)
    with pytest.raises(MoodleError):
        client.submissions(501)
