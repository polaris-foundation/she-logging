import datetime
import json
import logging

from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture
from flask_log_request_id import RequestID
from pytest_mock import MockFixture


def test_log_init(
    mocker: MockFixture,
    capsys: CaptureFixture,
) -> None:
    from she_logging import logging as my_logging

    mocker.patch.object(my_logging, "_initialised", False)
    mocker.patch.object(my_logging.root, "handlers", [])

    logger = my_logging.LogProxy("root")
    logger.info("hello world %s", 42, extra={"something": "12345"})

    captured = capsys.readouterr()

    assert len(my_logging.root.handlers) > 0

    log_object = json.loads(captured.out)
    assert log_object["requestID"] is None
    assert log_object["severity"] == "INFO"
    assert log_object["message"] == "hello world 42"


def test_log_double_init(caplog: LogCaptureFixture) -> None:
    from she_logging import logging as my_logging

    logger = my_logging.getLogger("root")

    with caplog.at_level(logging.INFO):
        logger.info("hello world %s", 42, extra={"something": "12345"})
        my_logging.init_logging()  # Extra init may generate warning, does not break logger
        logger.info("hello world %s", 42, extra={"something": "12345"})

    assert [
        record.levelno for record in caplog.records if record.levelno != logging.WARNING
    ] == [
        logging.INFO,
        logging.INFO,
    ]


def test_json_log(caplog: LogCaptureFixture) -> None:
    from she_logging import logger

    with caplog.at_level(logging.INFO):
        logger.info("hello world %s", 42, extra={"something": "12345"})

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.getMessage() == "hello world 42"
        assert record.something == "12345"
        assert record.requestID is None

        log_object = json.loads(caplog.text)
        assert log_object["requestID"] is None
        assert log_object["severity"] == "INFO"
        assert log_object["message"] == record.getMessage()


def test_log_objects(caplog: LogCaptureFixture) -> None:
    from she_logging import logger

    class Foo:
        def __repr__(self) -> str:
            return "<Foo>"

    time_now = datetime.datetime.now()
    date_now = datetime.date.today()

    with caplog.at_level(logging.INFO):
        logger.info(
            "Hello World",
            extra={"now": time_now, "date": date_now, "unserializable": Foo()},
        )

    log_object = json.loads(caplog.text)
    assert log_object["now"] == time_now.isoformat()
    assert log_object["date"] == date_now.isoformat()
    # Remove quotes in the assertion because the message format varies by Python version
    assert (
        log_object["unserializable"].replace("'", "")
        == "Object of type Foo is not JSON serializable <Foo>"
    )


def test_json_log_request(caplog: LogCaptureFixture) -> None:
    from flask import Flask

    from she_logging import logger

    app = Flask(__name__)
    RequestID(app)
    with caplog.at_level(logging.INFO):
        with app.test_request_context(
            "url", headers={"X-Client": "gdm-desktop", "X-Version": "19.1"}
        ):
            logger.info("hello world %s", 42, extra={"something": "12345"})

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert record.getMessage() == "hello world 42"
        assert record.something == "12345"
        assert record.requestID is None

        log_object = json.loads(caplog.text)
        assert log_object["requestID"] is None
        assert log_object["X-Client"] == "gdm-desktop"
        assert log_object["X-Version"] == "19.1"
        assert log_object["severity"] == "INFO"
        assert log_object["message"] == record.getMessage()
