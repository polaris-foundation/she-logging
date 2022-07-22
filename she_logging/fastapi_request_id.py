from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from she_logging.request_id import current_request_id, reset_request_id, set_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id_token = set_request_id(
            request.headers.get("X-Request-ID", None) or str(uuid4())
        )

        response = await call_next(request)
        request_id = current_request_id()
        if request_id is not None:
            response.headers["X-Request-ID"] = request_id
        reset_request_id(request_id_token)

        return response
