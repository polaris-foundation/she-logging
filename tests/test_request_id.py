import json

from _pytest.logging import LogCaptureFixture

from she_logging import request_id


def test_setting_request_id() -> None:
    assert request_id.current_request_id() is None

    token1 = request_id.set_request_id("1234")
    assert request_id.current_request_id() == "1234"

    token2 = request_id.set_request_id("5678")
    assert request_id.current_request_id() == "5678"

    request_id.reset_request_id(token2)
    assert request_id.current_request_id() == "1234"

    request_id.reset_request_id(token1)
    assert request_id.current_request_id() is None


def test_flask_request_id(dummy_flask_request_id: str) -> None:
    assert request_id.current_request_id() == dummy_flask_request_id

    token1 = request_id.set_request_id("1234")
    assert request_id.current_request_id() == "1234"
    request_id.reset_request_id(token1)
    assert request_id.current_request_id() == dummy_flask_request_id


def test_log_request_id(
    dummy_flask_request_id: str, capsys: object, caplog: LogCaptureFixture
) -> None:
    import logging

    with caplog.at_level(logging.INFO):
        logging.info("Hello World", extra={"test": 42})

    for record in caplog.records:
        # requestID is in record for text log messages
        assert record.requestID == dummy_flask_request_id

        # and in json object output for cloud logging
        log_object = json.loads(caplog.text)
        assert log_object["requestID"] == dummy_flask_request_id
