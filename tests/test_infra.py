from dataclasses import replace
import json
from unittest.mock import Mock
from urllib.error import HTTPError
from urllib.request import urlopen
import pytest
from infra.broker import Broker
from infra.config import Settings
from infra.health import Health


@pytest.mark.parametrize("changes", [{"course_id": 0}, {"interval": 0}, {"retry_delay_ms": -1},
                                    {"max_attempts": 0}, {"smtp_security": "invalid"},
                                    {"smtp_user": "a", "smtp_password": ""},
                                    {"smtp_user": "a", "smtp_password": "b", "smtp_security": "none"},
                                    {"moodle_url": "file:///secret"}, {"moodle_url": "https://a.test?token=b"},
                                    {"moodle_url": "https://user:pass@a.test"}, {"queue_prefix": "bad prefix"},
                                    {"moodle_token": ""}])
def test_bad_configuration(changes):
    with pytest.raises(ValueError):
        replace(Settings(), **changes).validate()


def test_settings_environment_and_secret_file(tmp_path, monkeypatch):
    token = tmp_path / "token"
    token.write_text("test-token\n")
    monkeypatch.setenv("MOODLE_TOKEN_FILE", str(token))
    monkeypatch.setenv("POLL_INTERVAL_SECONDS", "60")
    assert Settings.load().moodle_token == "test-token"
    assert Settings.load().interval == 60


def test_topology_and_persistent_confirmed_publish(settings):
    broker = Broker(settings)
    broker.channel = Mock()
    broker.declare()
    assert broker.channel.queue_declare.call_count == 3
    arguments = broker.channel.queue_declare.call_args.kwargs["arguments"]
    assert arguments["x-message-ttl"] == settings.retry_delay_ms
    assert arguments["x-dead-letter-routing-key"] == broker.main
    broker.channel.confirm_delivery.assert_called_once()
    broker.publish(b"{}", "42:501:101")
    params = broker.channel.basic_publish.call_args.kwargs
    assert params["mandatory"] is True
    assert params["properties"].delivery_mode == 2


def test_health_and_readiness():
    health = Health("test")
    server = health.start(0)
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        assert json.load(urlopen(base + "/health"))["service"] == "test"
        with pytest.raises(HTTPError) as error:
            urlopen(base + "/ready")
        assert error.value.code == 503
        health.success()
        assert json.load(urlopen(base + "/ready"))["ready"] is True
        with pytest.raises(HTTPError) as error:
            urlopen(base + "/not-found")
        assert error.value.code == 404
    finally:
        server.shutdown()
        server.server_close()
