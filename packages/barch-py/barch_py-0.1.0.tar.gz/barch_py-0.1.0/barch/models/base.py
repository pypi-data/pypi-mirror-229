"""Module for the base model."""

from __future__ import annotations
import attrs


@attrs.define()
class BaseModel:
    """The base model class from which all other models inherit."""
