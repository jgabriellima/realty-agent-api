import logging
from contextvars import ContextVar
from datetime import datetime
from typing import Optional
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


async def _aiter(data):
    yield data


CORRELATION_ID_HEADER = "Correlation-Id"

CORRELATION_ID_CTX_KEY = "correlation_id"
START_TIME_CTX_KEY = "start_time"
END_TIME_CTX_KEY = "end_time"
RESPONSE_DURATION_CTX_KEY = "response_duration"

_correlation_id_ctx_var: ContextVar[Optional[str]] = ContextVar(
    CORRELATION_ID_CTX_KEY, default=None
)
_start_time_ctx_var: ContextVar[Optional[datetime]] = ContextVar(START_TIME_CTX_KEY, default=None)
_end_time_ctx_var: ContextVar[Optional[datetime]] = ContextVar(END_TIME_CTX_KEY, default=None)
_response_duration_ctx_var: ContextVar[Optional[int]] = ContextVar(
    RESPONSE_DURATION_CTX_KEY, default=None
)


def get_correlation_id() -> Optional[str]:
    return _correlation_id_ctx_var.get() if _correlation_id_ctx_var else None


def get_start_time() -> Optional[datetime]:
    return _start_time_ctx_var.get() if _start_time_ctx_var else None


def get_end_time() -> Optional[datetime]:
    return _end_time_ctx_var.get() if _end_time_ctx_var else None


def get_response_duration() -> Optional[int]:
    return _response_duration_ctx_var.get() if _response_duration_ctx_var else None


class RequestContextLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        _correlation_id_ctx_var.set(request.headers.get(CORRELATION_ID_HEADER, str(uuid4())))
        correlation_id = get_correlation_id()
        start_time = datetime.utcnow()

        # Log request
        request_body = await request.body()
        request_headers = dict(request.headers)
        filtered_headers = {k: v for k, v in request_headers.items() if "token" in k.lower()}
        logger.info(
            f"Request: {request.method} {request.url} Headers: {filtered_headers} Body: {request_body.decode('utf-8')}"
        )

        response: Response = await call_next(request)

        response_body = [section async for section in response.__dict__["body_iterator"]]
        response_body = b"".join(response_body)
        logger.info(
            f"Response: {response.status_code} Headers: {dict(response.headers)} Body: {response_body.decode('utf-8')}"
        )

        response.__setattr__("body_iterator", _aiter(response_body))

        end_time = datetime.utcnow()
        if correlation_id is not None:
            response.headers[CORRELATION_ID_HEADER] = correlation_id
        response_duration = end_time - start_time
        _start_time_ctx_var.set(start_time)
        _end_time_ctx_var.set(end_time)
        _response_duration_ctx_var.set(response_duration.microseconds)
        return response
