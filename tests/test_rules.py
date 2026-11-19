from dataclasses import replace
from unittest.mock import Mock
import pytest
from acompanhamento.service import eligible, plain_text, run_cycle, scan, submitted_users

NOW = 1793977200


def task(**changes):
    return {"id": 501, "cmid": 1501, "course": 42, "name": "Projeto <b>ES II</b>",
            "duedate": NOW + 7200, "teamsubmission": 0, "nosubmissions": 0, "blindmarking": 0,
            "allowsubmissionsfromdate": 0, "cutoffdate": 0, **changes}


@pytest.mark.parametrize("delta,expected", [(1, True), (3600, True), (86400, True), (86401, False),
                                           (0, False), (-1, False), (-86400, False)])
def test_due_window(delta, expected):
    assert eligible(task(duedate=NOW + delta), {1501}, NOW, 42) is expected


@pytest.mark.parametrize("changes", [{"duedate": 0}, {"teamsubmission": 1}, {"nosubmissions": 1},
                                    {"blindmarking": 1}, {"course": 99}, {"cmid": 999},
                                    {"allowsubmissionsfromdate": NOW + 1}, {"cutoffdate": NOW},
                                    {"cutoffdate": NOW - 1}])
def test_out_of_scope(changes):
    assert not eligible(task(**changes), {1501}, NOW, 42)


def test_exact_opening_and_no_cutoff():
    assert eligible(task(allowsubmissionsfromdate=NOW, cutoffdate=0), {1501}, NOW, 42)


def test_latest_attempt_wins():
    assert submitted_users([{"userid": 1, "status": "submitted", "attemptnumber": 0},
                            {"userid": 1, "status": "reopened", "attemptnumber": 1},
                            {"userid": 2, "status": "submitted"}, {"userid": 3, "status": "draft"}]) == {2}


def test_time_breaks_tie():
    assert submitted_users([{"userid": 1, "status": "draft", "timemodified": 1},
                            {"userid": 1, "status": "submitted", "timemodified": 2}]) == {1}


def test_scan_pending_only(settings):
    moodle = Mock()
    moodle.assignments.return_value = [task(), task(id=502, cmid=1502, duedate=NOW-1)]
    moodle.visible_modules.return_value = {1501, 1502}
    moodle.students.return_value = [{"id": 1, "fullname": "Ana", "email": "ana@example.test"},
                                   {"id": 2, "fullname": "Bruno", "email": "bruno@example.test"},
                                   {"id": 3, "fullname": "Carla", "email": ""},
                                   {"id": 4, "fullname": "Davi", "email": "davi@example.test"}]
    moodle.submissions.return_value = [{"userid": 2, "status": "submitted"}, {"userid": 4, "status": "draft"}]
    events = scan(moodle, settings, NOW)
    assert [event.student_id for event in events] == [1, 4]
    assert events[0].assignment_name == "Projeto ES II"
    assert events[0].assignment_url.endswith("?id=1501")
    moodle.submissions.assert_called_once_with(501)


def test_empty_window_skips_student_query(settings):
    moodle = Mock()
    moodle.assignments.return_value = [task(duedate=0)]
    moodle.visible_modules.return_value = {1501}
    assert scan(moodle, settings, NOW) == []
    moodle.students.assert_not_called()


def test_no_partial_publish_when_api_fails(settings):
    moodle, broker = Mock(), Mock()
    moodle.assignments.return_value = [task(), task(id=502)]
    moodle.visible_modules.return_value = {1501}
    moodle.students.return_value = [{"id": 1, "fullname": "Ana", "email": "ana@example.test"}]
    moodle.submissions.side_effect = [[], RuntimeError("indisponível")]
    with pytest.raises(RuntimeError):
        run_cycle(moodle, broker, settings, NOW)
    broker.publish.assert_not_called()


def test_cycle_publishes_with_key(settings):
    moodle, broker = Mock(), Mock()
    moodle.assignments.return_value = [task()]
    moodle.visible_modules.return_value = {1501}
    moodle.students.return_value = [{"id": 1, "fullname": "Ana", "email": "ana@example.test"}]
    moodle.submissions.return_value = []
    events = run_cycle(moodle, broker, settings, NOW)
    broker.publish.assert_called_once_with(events[0].encode(), "42:501:1")


def test_clean_html():
    assert plain_text(" <b>Projeto</b> &amp;\n prática ") == "Projeto & prática"
