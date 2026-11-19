from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import smtplib
import sqlite3
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock
import pytest
from notificacoes.mailer import SmtpMailer, build_message, permanent_failure
from notificacoes.service import Handler
from notificacoes.store import Store


def test_completed_event_is_not_sent_twice(event, settings):
    store, mailer = Store(settings.database), Mock()
    assert store.process(event, mailer).status == "sent"
    assert store.process(event, mailer).status == "duplicate"
    assert mailer.send.call_count == 1


def test_history_survives_process_restart(event, settings):
    mailer = Mock()
    Store(settings.database).process(event, mailer)
    assert Store(settings.database).process(event, mailer).status == "duplicate"
    assert mailer.send.call_count == 1


def test_concurrent_consumers_share_idempotency(event, settings):
    store, mailer = Store(settings.database), Mock()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: store.process(event, mailer), range(2)))
    assert sorted(r.status for r in results) == ["duplicate", "sent"]
    assert mailer.send.call_count == 1


def test_expired_in_queue_is_ignored(event, settings):
    mailer = Mock()
    assert Store(settings.database).process(event, mailer, now=event.due_at).status == "expired"
    mailer.send.assert_not_called()


def test_fail_then_retry_success_and_audit(event, settings):
    store, mailer = Store(settings.database), Mock()
    mailer.send.side_effect = [ConnectionRefusedError(), None]
    first, second = store.process(event, mailer), store.process(event, mailer)
    assert (first.status, first.attempts, second.status, second.attempts) == ("retry", 1, "sent", 2)
    with sqlite3.connect(settings.database) as db:
        assert db.execute("SELECT outcome FROM audit ORDER BY id").fetchall() == [("retry",), ("sent",)]
        assert db.execute("SELECT error_type FROM audit WHERE outcome='retry'").fetchone()[0] == "ConnectionRefusedError"


def test_max_attempts_persist_across_duplicates(event, settings):
    store, mailer = Store(settings.database), Mock()
    mailer.send.side_effect = TimeoutError()
    assert [store.process(event, mailer, 3).status for _ in range(5)] == ["retry", "retry", "dead", "dead", "dead"]
    assert mailer.send.call_count == 3


def test_permanent_smtp_failure_is_dead_immediately(event, settings):
    mailer = Mock()
    mailer.send.side_effect = smtplib.SMTPDataError(550, b"refused")
    assert Store(settings.database).process(event, mailer).status == "dead"


@pytest.mark.parametrize("error,expected", [(smtplib.SMTPDataError(450, b"temporary"), False),
                                          (smtplib.SMTPAuthenticationError(535, b"auth"), True),
                                          (smtplib.SMTPRecipientsRefused({"x": (550, b"unknown")}), True),
                                          (smtplib.SMTPRecipientsRefused({"x": (450, b"busy")}), False),
                                          (ConnectionError(), False)])
def test_smtp_classification(error, expected):
    assert permanent_failure(error) is expected


def test_plain_and_html_email(event, settings):
    event = replace(event, student_name="Ana <teste>", assignment_name="Projeto & prática")
    msg = build_message(event, settings)
    assert msg["To"] == event.student_email
    assert msg["X-Reengajamento-ID"] == event.event_id
    assert event.assignment_url in msg.get_body(preferencelist=("plain",)).get_content()
    html = msg.get_body(preferencelist=("html",)).get_content()
    assert "Ana &lt;teste&gt;" in html
    assert "Projeto &amp; prática" in html
    assert "America/Sao_Paulo" in html
    assert build_message(event, settings)["Message-ID"] == msg["Message-ID"]


@pytest.mark.parametrize("security,factory", [("none", "SMTP"), ("starttls", "SMTP"), ("ssl", "SMTP_SSL")])
def test_smtp_real_adapter_configuration(event, settings, monkeypatch, security, factory):
    constructor = MagicMock()
    server = constructor.return_value.__enter__.return_value
    server.send_message.return_value = {}
    monkeypatch.setattr(smtplib, factory, constructor)
    configured = replace(settings, smtp_security=security,
                         smtp_user="user" if security != "none" else "",
                         smtp_password="secret" if security != "none" else "")
    SmtpMailer(configured).send(event)
    server.send_message.assert_called_once()
    assert server.starttls.call_count == (1 if security == "starttls" else 0)
    assert server.login.call_count == (1 if security != "none" else 0)


def test_ack_only_after_successful_retry_publish(event, settings):
    broker, channel, store = Mock(), Mock(), Mock()
    broker.retry = "retry"
    store.process.return_value = SimpleNamespace(status="retry", attempts=1, error_type="TimeoutError")
    broker.publish.side_effect = RuntimeError("broker unavailable")
    handler = Handler(broker, store, Mock(), settings)
    with pytest.raises(RuntimeError):
        handler(channel, SimpleNamespace(delivery_tag=7), None, event.encode())
    channel.basic_ack.assert_not_called()


def test_invalid_message_goes_to_dead_queue_before_ack(settings):
    broker, channel, store = Mock(), Mock(), Mock()
    broker.dead = "dead"
    Handler(broker, store, Mock(), settings)(channel, SimpleNamespace(delivery_tag=1), None, b"invalid")
    broker.publish.assert_called_once_with(b"invalid", queue="dead")
    channel.basic_ack.assert_called_once_with(delivery_tag=1)
    store.process.assert_not_called()


@pytest.mark.parametrize("status,route", [("sent", None), ("duplicate", None), ("expired", None), ("retry", "retry"), ("dead", "dead")])
def test_consumer_routes_result_then_acks(event, settings, status, route):
    broker, channel, store = Mock(), Mock(), Mock()
    broker.retry, broker.dead = "retry", "dead"
    store.process.return_value = SimpleNamespace(status=status, attempts=1, error_type="")
    Handler(broker, store, Mock(), settings)(channel, SimpleNamespace(delivery_tag=9), None, event.encode())
    channel.basic_ack.assert_called_once_with(delivery_tag=9)
    if route:
        broker.publish.assert_called_once_with(event.encode(), event.event_id, route)
    else:
        broker.publish.assert_not_called()
