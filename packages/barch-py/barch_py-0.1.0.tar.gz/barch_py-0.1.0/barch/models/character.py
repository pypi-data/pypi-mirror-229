"""Module for Character model."""

from __future__ import annotations
from typing import Any

from .base import BaseModel
from barch.enums import Position, Role, Rarity

import attrs

__all__ = (
    "Character",
    "Terrain",
    "BaseCharacter",
    "TerrainDetails",
    "CharacterInfo",
    "Image",
    "CharacterDetails",
    "Stats",
    "CommonModel",
    "Skills",
    "Characters",
)


@attrs.define(init=False)
class BaseCharacter(BaseModel):
    """Represents base character model."""

    name: str
    """Name of the character."""

    profile: str
    """Profile description of the character."""

    rarity: Rarity
    """Rarity of the character."""

    base_star: int
    """Base star."""

    position: Position
    """Position of the character."""

    role: Role
    """Role of the character."""

    armor_type: str
    """Armor type of the character."""

    bullet_type: str
    """Bullet type of the character."""

    weapon_type: str
    """Weapon type of the character."""

    squad_type: str
    """Squad type."""


@attrs.define(init=False)
class Character(BaseCharacter):
    """Represents character model."""

    id: int
    """Id of the character."""

    school: str
    """The school to which the character belongs to."""

    terrain: Terrain
    """The terrain details."""


@attrs.define(init=False)
class CharacterInfo(BaseModel):
    """Represents CharacterInfo model."""

    age: int
    # TODO: string to int
    """The age of the character."""

    birth_date: str
    """The birth date of the character."""

    height: str
    """The height of the character."""

    artist: str
    """The designer or illustrator of the character."""

    club: str
    """The club to which the character belongs."""

    school: str
    """The school to which the character belongs."""

    school_year: str
    """The school year of the character."""

    voice_actor: str
    """The voice actor of the character."""


@attrs.define
class Image(BaseModel):
    """Represents image model."""

    icon: str

    lobby: str

    portrait: str


@attrs.define(init=False)
class CharacterDetails(BaseModel):
    """Represents Character Details model."""

    id: int

    is_released: bool

    is_playable: bool

    character: BaseCharacter

    info: CharacterInfo

    image: Image

    stat: Stats

    terrain: Terrain

    skills: Skills


@attrs.define(init=False)
class Terrain(BaseModel):
    """Represents Terrain model."""

    urban: TerrainDetails

    outdoor: TerrainDetails

    indoor: TerrainDetails


@attrs.define
class TerrainDetails(BaseModel):
    """Represents TerrainDetails model."""

    damage_dealt: str

    shield_block_rate: str


@attrs.define(init=False)
class Stats(BaseModel):
    """Represents Stats model."""

    id: int

    attack_level1: int

    attack_level100: int

    max_hp_level1: int

    max_hp_level100: int

    defense_level1: int

    defense_level100: int

    heal_power_level1: int

    heal_power_level100: int

    def_penetrate_level1: int

    def_penetrate_level100: int

    ammo_count: int

    ammo_cost: int

    range: int

    move_speed: int

    street_mood: str

    outdoor_mood: str

    indoor_mood: str


@attrs.define
class CommonModel(BaseModel):
    """Represents a CommonModel model which is used in multiple classes."""

    id: int

    name: str

    description: str


@attrs.define(init=False)
class Skills(BaseModel):
    """Represents Skills model."""

    ex: list[CommonModel] | None = attrs.field(default=None)

    normal: list[CommonModel] | None = attrs.field(default=None)

    passive: list[CommonModel] | None = attrs.field(default=None)

    sub: list[CommonModel] | None = attrs.field(default=None)


@attrs.define
class Characters(BaseModel):
    """Represents Characters model."""

    id: int

    name: str
