from typing import Dict, Optional

from fastapi import FastAPI
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from she_logging import logger
from she_logging.fastapi_request_id import RequestContextMiddleware

app = FastAPI()
app.add_middleware(RequestContextMiddleware)


@app.middleware("http")
async def log_requests(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    request_details: Dict[str, str] = {}
    response = await call_next(request)
    logger.info(
        '%s "%s" %s',
        request.method,
        request.base_url,
        response.status_code,
        extra={"httpRequest": request_details},
    )
    return response


@app.get("/")
async def read_root() -> dict:
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None) -> dict:
    return {"item_id": item_id, "q": q}
