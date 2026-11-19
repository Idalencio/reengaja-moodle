from dataclasses import replace
import time
import pytest
from infra.config import Settings
from infra.events import Reminder


@pytest.fixture
def settings(tmp_path):
    return replace(Settings(), database=str(tmp_path / "deliveries.sqlite3"))


@pytest.fixture
def event():
    now = int(time.time())
    return Reminder(42, 501, 101, "Ana Exemplo", "ana@example.test", "Projeto ES II", now + 7200,
                    "https://moodle.example.test/mod/assign/view.php?id=1501", now)
