"""Module for HTTP response models."""

from __future__ import annotations

from typing import Any
import attrs

from .base import BaseModel

__all__ = ("HttpSuccessResponse", "HttpErrorResponse")


@attrs.define()
class HttpSuccessResponse(BaseModel):
    """Represents HTTP sucess response."""

    status: int
    """The HTTP status code."""

    message: str
    """The success response message."""

    data: Any
    """The JSON API response."""


@attrs.define()
class HttpErrorResponse(BaseModel):
    """Represents HTTP error response."""

    status: int
    """HTTP error status code."""

    message: str
    """The error response message."""
