import json
import logging
import sys
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class JSONStructuredFormatter(logging.Formatter):
    """JSON log formatter for enterprise observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_structured_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONStructuredFormatter())
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware attaching request_id and logging HTTP execution time."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        logging.getLogger("app.request").info(
            f"{request.method} {request.url.path} - {response.status_code} ({duration_ms}ms)",
            extra={"request_id": request_id},
        )
        return response
