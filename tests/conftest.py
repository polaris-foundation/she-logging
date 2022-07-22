from uuid import uuid4

import pytest
from _pytest import logging as pytest_logging
from _pytest.config import Config
from _pytest.monkeypatch import MonkeyPatch

from she_logging import request_id
from she_logging.logging import CustomisedJSONFormatter


class TestLoggingPlugin(pytest_logging.LoggingPlugin):
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.formatter = CustomisedJSONFormatter()


def pytest_configure(config: Config) -> None:
    config.pluginmanager.get_plugin("logging").LoggingPlugin = TestLoggingPlugin


@pytest.fixture
def dummy_flask_request_id(monkeypatch: MonkeyPatch) -> str:
    request_uuid = str(uuid4())

    def dummy_request_id() -> str:
        return request_uuid

    monkeypatch.setattr(request_id, "FLASK_AVAILABLE", True)
    monkeypatch.setattr(request_id, "flask_request_id", dummy_request_id)
    return request_uuid
