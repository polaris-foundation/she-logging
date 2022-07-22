import json
import logging
from typing import Dict, Optional

import pytest
from _pytest.logging import LogCaptureFixture
from fastapi import FastAPI
from fastapi.testclient import TestClient

from she_logging.fastapi_request_id import RequestContextMiddleware
from she_logging.request_id import current_request_id


@pytest.fixture
def fastapi() -> FastAPI:
    app = FastAPI(docs_url="/ui", title="She logging tests", version="0.0.1")
    app.add_middleware(RequestContextMiddleware)

    @app.get("/testme", summary="Check the service is running", tags=["infra"])
    async def running() -> Dict[str, Optional[str]]:
        from she_logging import logger

        logger.info("testme endpoint")
        return {"request_id": current_request_id()}

    return app


@pytest.fixture
def client(fastapi: FastAPI) -> TestClient:
    client = TestClient(fastapi)
    return client


def test_fastapi_request_id(client: TestClient, caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        response = client.get("/testme", headers={"X-Request-ID": "999-888-777"})
    assert response.status_code == 200
    assert response.json()["request_id"] == "999-888-777"
    captured = json.loads(caplog.text)
    assert captured["message"] == "testme endpoint"
