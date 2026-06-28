"""Shared Pydantic schemas (API contracts).

These models define the *shape* of data crossing the HTTP boundary. They live
in the presentation/boundary layer and are deliberately kept separate from
domain entities so transport concerns never leak into business logic.
"""

from enum import Enum

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Coarse service health state."""

    OK = "ok"
    DEGRADED = "degraded"


class RootResponse(BaseModel):
    """Service metadata returned by `GET /`."""

    name: str = Field(..., description="Human-readable application name")
    version: str = Field(..., description="Running application version")
    environment: str = Field(..., description="Active deployment environment")
    docs_url: str = Field(..., description="Path to the interactive API docs")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "AI Travel Planner",
                "version": "0.1.0",
                "environment": "development",
                "docs_url": "/docs",
            }
        }
    }


class HealthResponse(BaseModel):
    """Liveness/readiness payload returned by `GET /health`."""

    status: HealthStatus = Field(..., description="Overall service status")
    version: str = Field(..., description="Running application version")
    environment: str = Field(..., description="Active deployment environment")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "version": "0.1.0",
                "environment": "development",
            }
        }
    }


class ErrorDetail(BaseModel):
    """A single field-level error (used for validation failures)."""

    field: str = Field(..., description="Location of the offending input")
    message: str = Field(..., description="Why the value was rejected")


class ErrorResponse(BaseModel):
    """Uniform error envelope returned for every handled failure."""

    error: str = Field(..., description="Stable, machine-readable error code")
    message: str = Field(..., description="Human-readable explanation")
    details: list[ErrorDetail] | None = Field(
        default=None, description="Optional field-level breakdown"
    )
    request_id: str | None = Field(
        default=None, description="Correlation id for tracing this request"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "not_found",
                "message": "The requested resource does not exist.",
                "details": None,
                "request_id": "0f9c2a1e-...",
            }
        }
    }
