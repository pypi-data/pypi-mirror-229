"""Module for models related to raid."""

from __future__ import annotations
from datetime import datetime

import attrs

from .base import BaseModel

__all__ = ("Raid", "Raids")


@attrs.define(init=False)
class Raid(BaseModel):
    """Represents Raid model which contains individual raid details.."""

    season_id: int | None = attrs.field(default=None)

    boss_name: str | None = attrs.field(default=None)

    start_at: datetime | None = attrs.field(default=None)

    settle_at: datetime | None = attrs.field(default=None)

    end_at: datetime | None = attrs.field(default=None)


@attrs.define(init=False)
class Raids(BaseModel):
    """Represents Raids model."""

    current: list[Raid] | None = attrs.field(default=None)

    upcoming: list[Raid] | None = attrs.field(default=None)

    ended: list[Raid] | None = attrs.field(default=None)
