from contextvars import ContextVar, Token
from typing import Any, Optional

try:
    from flask_log_request_id import current_request_id as flask_request_id
except ImportError:
    FLASK_AVAILABLE = False
    flask_request_id = None
else:
    FLASK_AVAILABLE = True


REQUEST_ID_UNSET = object()


_request_id_context_var: ContextVar = ContextVar("requestID", default=REQUEST_ID_UNSET)


def current_request_id() -> Optional[str]:
    """Returns request ID as set in current context,
    otherwise returns flask request ID if we have flask
    otherwise returns None
    """
    request_id: Any = _request_id_context_var.get()

    if request_id is REQUEST_ID_UNSET:
        if FLASK_AVAILABLE:
            request_id = flask_request_id()
        else:
            request_id = None

    return request_id


def set_request_id(requestId: str) -> Token:
    """Set the current request ID, returns a token"""
    return _request_id_context_var.set(requestId)


def reset_request_id(token: Token) -> None:
    """Reset the request ID using the token returned from set_request_id"""
    _request_id_context_var.reset(token)
