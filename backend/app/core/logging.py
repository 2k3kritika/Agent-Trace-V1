"""Structured application logging.

The logging format is JSON-compatible so local logs remain readable while
CloudWatch can consume the same records without requiring a separate logging
architecture.
"""

import json
import logging
import sys
import time
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from app.core.constants import REQUEST_ID_HEADER


_request_id: ContextVar[str | None] = ContextVar(
    "agenttrace_request_id",
    default=None,
)


class JsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    RESERVED_FIELDS = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Serialize a log record into one JSON object."""

        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = _request_id.get()

        if request_id:
            payload["request_id"] = request_id

        for key, value in record.__dict__.items():
            if key not in self.RESERVED_FIELDS and not key.startswith("_"):
                try:
                    json.dumps(value)
                    payload[key] = value
                except (TypeError, ValueError):
                    payload[key] = str(value)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )


def set_request_id(request_id: str | None) -> None:
    """Set the request ID for the current execution context."""

    _request_id.set(request_id)


def get_request_id() -> str | None:
    """Return the request ID associated with the current execution context."""

    return _request_id.get()


def configure_logging(level: str = "INFO") -> None:
    """Configure root application logging."""

    root_logger = logging.getLogger()

    numeric_level = getattr(
        logging,
        level.upper(),
        logging.INFO,
    )

    root_logger.setLevel(numeric_level)

    # Avoid installing duplicate handlers when tests or reloaders initialize
    # the application more than once.
    if not any(
        isinstance(handler.formatter, JsonFormatter)
        for handler in root_logger.handlers
    ):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        root_logger.addHandler(handler)

    # Keep noisy framework logs useful but structured.
    for logger_name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "sqlalchemy.engine",
    ):
        framework_logger = logging.getLogger(logger_name)
        framework_logger.setLevel(numeric_level)


def get_logger(name: str) -> logging.Logger:
    """Return an application logger."""

    return logging.getLogger(name)


class RequestLoggingMiddleware:
    """ASGI middleware for request IDs and request timing.

    This middleware is intentionally dependency-light and can be used both
    with local Uvicorn/FastAPI and an AWS Lambda ASGI adapter.
    """

    def __init__(self, app: Any) -> None:
        self.app = app
        self.logger = get_logger("agenttrace.http")

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Any,
        send: Any,
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request_id = self._get_request_id(scope)
        set_request_id(request_id)

        start = time.perf_counter()

        status_code: int | None = None

        async def send_wrapper(message: dict[str, Any]) -> None:
            nonlocal status_code

            if message.get("type") == "http.response.start":
                status_code = int(message.get("status", 500))

                headers = list(message.get("headers", []))

                request_id_bytes = REQUEST_ID_HEADER.lower().encode()

                if not any(
                    key.lower() == request_id_bytes
                    for key, _ in headers
                ):
                    headers.append(
                        (
                            request_id_bytes,
                            request_id.encode(),
                        )
                    )

                message["headers"] = headers

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round(
                (time.perf_counter() - start) * 1000,
                2,
            )

            self.logger.info(
                "HTTP request completed",
                extra={
                    "route": scope.get("path"),
                    "method": scope.get("method"),
                    "status": status_code or 500,
                    "duration_ms": duration_ms,
                },
            )

            set_request_id(None)

    @staticmethod
    def _get_request_id(scope: dict[str, Any]) -> str:
        """Read an incoming request ID or generate one."""

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }

        incoming = headers.get(REQUEST_ID_HEADER.lower())

        if incoming:
            return incoming

        # Local import prevents the logging module from depending on the
        # application ID helper during startup.
        import uuid

        return f"req_{uuid.uuid4().hex}"