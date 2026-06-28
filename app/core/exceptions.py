"""Application exception hierarchy.

A single base `AppException` carries an HTTP status, a stable machine-readable
`code`, and a human message. Use cases and services raise these *domain-aware*
errors; the registered handlers (see `app.core.error_handlers`) translate them
into the uniform `ErrorResponse` envelope. This keeps business code free of
FastAPI/HTTP details — it just raises meaningful errors.
"""

from __future__ import annotations


class AppException(Exception):
    """Base class for all expected, handled application errors."""

    status_code: int = 500
    code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    """A requested resource does not exist."""

    status_code = 404
    code = "not_found"
    message = "The requested resource does not exist."


class ValidationError(AppException):
    """Input failed domain-level validation (beyond schema checks)."""

    status_code = 422
    code = "validation_error"
    message = "The request could not be validated."


class ConflictError(AppException):
    """The request conflicts with current resource state."""

    status_code = 409
    code = "conflict"
    message = "The request conflicts with the current state."


class ExternalServiceError(AppException):
    """A downstream dependency (LLM, DB, 3rd-party API) failed."""

    status_code = 502
    code = "external_service_error"
    message = "An upstream service failed to respond."
