"""Module to serialize and deserialize JSON data and models."""

from __future__ import annotations
from typing import TypeVar, Any
from datetime import datetime

from barch.models import (
    Character,
    Terrain,
    TerrainDetails,
    CharacterDetails,
    CharacterInfo,
    Image,
    Stats,
    Skills,
    CommonModel,
    BaseCharacter,
    Characters,
    Raid,
    Raids,
)
from barch.enums import Position, Role, Rarity

T = TypeVar("T")

__all__ = ("Serializer",)


class Serializer:
    """Deserializes JSON data to models."""

    __slots__ = ()

    def _datetime_from_unix_ms(self, datetime_str: str | int | None) -> datetime | None:
        """Converts unix timestamp in milliseconds to UTC datetime."""

        return datetime.utcfromtimestamp(datetime_str / 1000) if datetime_str else None

    def _to_camel_case(self, attr: str) -> str:
        """Converts input arguments to camel case."""
        first, *rest = attr.split("_")
        return "".join((first.lower(), *map(str.title, rest)))

    def _set_attrs(
        self, model: Any, data: dict[str, Any], *attrs: str, camel_case: bool = False
    ) -> None:
        """Generate model from JSON payload."""

        if data:
            for attr in attrs:
                cased_attr = self._to_camel_case(attr) if camel_case else attr

                if data.get(cased_attr) is not None:
                    setattr(model, attr, data[cased_attr])
                else:
                    setattr(model, attr, None)

    def _set_attrs_cased(self, model: Any, data: dict[str, Any], *attrs: str) -> None:
        """Generate model from JSON payload when input arguments need to be changed to camel case."""

        return self._set_attrs(model, data, *attrs, camel_case=True)

    def _deserialize_terrain(self, data: dict[str, Any]) -> Terrain:
        """Deserializes JSON payload into `Terrain` model."""

        terrain = Terrain()

        terrain.urban = self._deserialize_terrain_details(data.get("urban", {}))
        terrain.outdoor = self._deserialize_terrain_details(data.get("outdoor", {}))
        terrain.indoor = self._deserialize_terrain_details(data.get("indoor", {}))

        return terrain

    def _deserialize_terrain_details(self, data: dict[str, Any]) -> TerrainDetails:
        """Deserializes JSON payload into `TerrainDetails` model."""

        terrain_details = TerrainDetails(
            data.get("DamageDealt", ""), data.get("ShieldBlockRate", "")
        )

        return terrain_details

    def deserialize_character(self, data: dict[str, Any]) -> Character:
        """Deserializes JSON payload into `Character` model."""

        character = Character()

        character.position = Position.from_str(data.get("position", None))
        character.role = Role.from_str(data.get("role", None))
        character.rarity = Rarity.try_from_str(data.get("rarity", None))

        character.terrain = self._deserialize_terrain(data.get("terrain", {}))

        self._set_attrs_cased(
            character,
            data,
            "id",
            "name",
            "profile",
            "base_star",
            "armor_type",
            "bullet_type",
            "weapon_type",
            "squad_type",
            "school",
        )

        return character

    def deserialize_character_info(self, data: dict[str, Any]) -> CharacterInfo:
        """Deserializes JSON payload into `CharacterInfo` model."""

        charcter_info = CharacterInfo()

        self._set_attrs_cased(
            charcter_info,
            data,
            "age",
            "birth_date",
            "height",
            "artist",
            "club",
            "school",
            "school_year",
            "voice_actor",
        )

        return charcter_info

    def deserialize_stats(self, data: dict[str, Any]) -> Stats:
        """Deserializes JSON payload into `Stats` model."""

        character_stats = Stats()

        self._set_attrs_cased(
            character_stats,
            data,
            "id",
            "attack_level1",
            "attack_level100",
            "defense_level1",
            "defense_level100",
            "heal_power_level1",
            "heal_power_level100",
            "def_penetrate_level1",
            "def_penetrate_level100",
            "ammo_count",
            "ammo_cost",
            "range",
            "move_speed",
            "street_mood",
            "outdoor_mood",
            "indoor_mood",
        )

        setattr(character_stats, "max_hp_level1", data["maxHPLevel1"])
        setattr(character_stats, "max_hp_level100", data["maxHPLevel100"])

        return character_stats

    def deserialize_skills_details(self, data: dict[str, Any]) -> CommonModel:
        """Deserializes JSON payload into `CommonModel` model."""

        return [
            CommonModel(skill.get("id"), skill.get("name"), skill.get("description", ""))
            for skill in data
        ]

    def deserialize_skills(self, data: dict[str, Any]) -> Skills:
        """Deserializes JSON payload into `Skills` model."""

        character_skills = Skills()

        character_skills.ex = (
            self.deserialize_skills_details(data.get("ex", [])[0])
            if data.get("ex", None)
            else None
        )

        character_skills.normal = (
            self.deserialize_skills_details(data.get("normal", [])[0])
            if data.get("normal", None)
            else None
        )

        character_skills.passive = (
            self.deserialize_skills_details(data.get("passive", [])[0])
            if data.get("passive", None)
            else None
        )

        character_skills.sub = (
            self.deserialize_skills_details(data.get("sub", [])[0])
            if data.get("sub", None)
            else None
        )

        return character_skills

    def deserialize_image(self, data: dict[str, Any]) -> Image:
        """Deserializes JSON payload into `Image` model."""

        return Image(
            data.get("icon", ""),
            data.get("portrait", ""),
            data.get("lobby", ""),
        )

    def deserialize_base_character(self, data: dict[str, Any]) -> BaseCharacter:
        """Deserializes JSON payload into `BaseCharacter` model."""

        character = BaseCharacter()

        character.position = Position.from_str(data.get("position", None))
        character.role = Role.from_str(data.get("role", None))
        character.rarity = Rarity.try_from_str(data.get("rarity", None))

        self._set_attrs_cased(
            character,
            data,
            "name",
            "profile",
            "base_star",
            "armor_type",
            "bullet_type",
            "weapon_type",
            "squad_type",
        )

        return character

    def deserialize_character_details(self, data: dict[str, Any]) -> CharacterDetails:
        """Deserializes JSON payload into `CharacterDetails` model."""

        charcter_details = CharacterDetails()

        charcter_details.character = self.deserialize_base_character(data.get("character", {}))

        charcter_details.info = self.deserialize_character_info(data.get("info", {}))
        charcter_details.stat = self.deserialize_stats(data.get("stat", {}))
        charcter_details.terrain = self._deserialize_terrain(data.get("terrain", {}))

        charcter_details.image = self.deserialize_image(data.get("image", {}))

        charcter_details.skills = self.deserialize_skills(data.get("skills", {}))

        self._set_attrs_cased(charcter_details, data, "id", "is_released", "is_playable")

        return charcter_details

    def deserialize_characters_from_query(self, data: dict[str, Any]) -> Characters:
        """Deserializes JSON payload into `Characters` model."""

        return Characters(data.get("id"), data.get("name"))

    def deserialize_raid(self, data: dict[str, Any]) -> Raid:
        """Deserializes JSON payload into `Raid` model."""

        raid = Raid()

        raid.start_at = self._datetime_from_unix_ms(data.get("startAt", None))
        raid.settle_at = self._datetime_from_unix_ms(data.get("settleAt", None))
        raid.end_at = self._datetime_from_unix_ms(data.get("endAt", None))

        self._set_attrs_cased(raid, data, "season_id", "boss_name")

        return raid

    def deserialize_raids(self, data: dict[str, Any]) -> Raids:
        """Deserializes JSON payload into `Raids` model."""

        raids = Raids()
        raids.current = [self.deserialize_raid(raid) for raid in data.get("current", [])]

        raids.upcoming = [self.deserialize_raid(raid) for raid in data.get("upcoming", [])]

        raids.ended = [self.deserialize_raid(raid) for raid in data.get("ended", [])]

        return raids
