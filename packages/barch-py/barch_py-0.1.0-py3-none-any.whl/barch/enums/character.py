"""Module for all the enums related to character."""

from __future__ import annotations

from .base import BaseEnum

__all__ = ("Position", "Role", "Rarity")


class Position(BaseEnum):
    """Represents position of the character."""

    Back = "Back"

    Front = "Front"

    Middle = "Middle"


class Role(BaseEnum):
    """Represents role of the character."""

    Dealer = "Dealer"

    Healer = "Healer"

    Support = "Support"

    Tank = "Tank"

    TacticalSupport = "T.S."


class Rarity(BaseEnum):
    """Represents the rarity of the character."""

    Rare = "R"

    SuperRare = "SR"

    SuperSuperRare = "SSR"
