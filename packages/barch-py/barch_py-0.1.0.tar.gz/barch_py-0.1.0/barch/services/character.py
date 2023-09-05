"""Moduke for character related services."""

from __future__ import annotations
from typing import TypeVar

from .base import BaseService
from barch.models import (
    HttpErrorResponse,
    Character,
    CharacterDetails,
    Characters,
)
from barch.enums import Role, Position
from barch import endpoints
from barch.result import Result, Success, Error


T = TypeVar("T")
ValueT = TypeVar("ValueT")
ResultT = Result[ValueT, HttpErrorResponse]

__all__ = ("CharacterService",)


class CharacterService(BaseService):
    """The service that handles all the methods related to characters."""

    __slots__ = ()

    async def _get_all_characters(
        self, is_jp: bool = False
    ) -> ResultT[list[Character]]:
        """Internal method for getting all character details which is used by the
        EN and JP version service methods.

        Keyword Args:
            is_jp: the optional boolean flag, which specifies if the character details need to be fetched
                in EN or JP version.

        Returns:
            [`Result`][barch.Result] containing `list[Character]` on success or error data on error.
        """

        if is_jp:
            route = endpoints.GET_ALL_CHARACTERS_JP.generate_route()
        else:
            route = endpoints.GET_ALL_CHARACTERS.generate_route()

        result = await self._http.fetch(route)

        if isinstance(result, HttpErrorResponse):
            return Error(result)

        return Success(
            [self._serializer.deserialize_character(element) for element in result.data]
        )

    async def get_all_characters(self) -> ResultT[list[Character]]:
        """Get all the characters with details EN version.

        Returns:
            [`Result`][barch.Result] containing `list[Character]` on success or error data on error.

        ??? example

            ```py
            from barch import Client

            client = Client()

            result = await client.character.get_all_characters()

            if result.is_success:
                characters = result.value

            if result.is_error:
                error = result.error

            await client.close()
            ```
        """

        return await self._get_all_characters()

    async def get_all_characters_jp(self) -> ResultT[list[Character]]:
        """Get all the characters with details japanese version.

        Returns:
            [`Result`][barch.Result] containing `list[Character]` on success or error data on error.

        ??? example

            ```py
            from barch import Client

            client = Client()

            result = await client.character.get_all_characters_jp()

            if result.is_success:
                characters = result.value

            if result.is_error:
                error = result.error

            await client.close()
        """

        return await self._get_all_characters(is_jp=True)

    async def _get_character(
        self, name: str | None = None, id: int | None = None, is_jp: bool = False
    ) -> ResultT[CharacterDetails]:
        """Internal method used to get a single character details, which is used by both EN and JP versions.

        Keyword Args:
            name: The optional name of the chracter either for EN and JP version.

            id: The optional id of the character.

            is_jp: The optional is_jp flag which specifies if the character details need to be fetched in EN or JP version.

        Returns:
            [`Result`][barch.Result] containing `CharacterDetails` on success or error data on error.

        """

        params: dict = {}

        if id:
            params.update({"id": "true"})

        if is_jp:
            route = endpoints.GET_CHARACTER_JP.generate_route(
                name if name else id
            ).with_params(params if params else None)

        else:
            route = endpoints.GET_CHARACTER.generate_route(
                name if name else id
            ).with_params(params if params else None)

        result = await self._http.fetch(route)

        if isinstance(result, HttpErrorResponse):
            return Error(result)

        return Success(self._serializer.deserialize_character_details(result.data))

    async def get_character(
        self, name: str | None = None, id: int | None = None
    ) -> ResultT[CharacterDetails]:
        """Get a single character either by name or id, EN version.
        Atleast one parameter, either name or id need to be specified.

        Keyword Args:
            name: The optional name of the character.
            id: The optional id of the character.

        Returns:
            [`Result`][barch.Result] containing `CharacterDetails]` on success or error data on error.

        Raises:
            ValueError: When no arguments are given

        ??? example

            ```py
            from barch import Client

            client = Client()

            result = await client.character.get_character(id=10000)

            if result.is_success:
                characters = result.value

            if result.is_error:
                error = result.error

            await client.close()
            ```
        """

        if name or id:
            return await self._get_character(name=name, id=id)

        else:
            raise ValueError("Atleast one parameter must be specified.")

    async def get_character_jp(
        self, name: str | None = None, id: int | None = None
    ) -> ResultT[CharacterDetails]:
        """Get a single character either by name or id, JP version.
        Atleast one parameter, either name or id need to be specified.

        Keyword Args:
            name: The optional name of the character. Note that the character input name needs to be JP.
            id: The optional id of the character.

        Returns:
            [`Result`][barch.Result] containing `CharacterDetails` on success or error data on error.

        ??? example

            ```py
            from barch import Client

            client = Client()

            result = await client.character.get_character_jp(id=10000)

            if result.is_success:
                characters = result.value

            if result.is_error:
                error = result.error

            await client.close()
            ```"""

        return await self._get_character(name=name, id=id, is_jp=True)

    async def get_character_by_query(
        self,
        role: Role | None = None,
        type: str | None = None,
        school: str | None = None,
        club: str | None = None,
        position: Position | None = None,
        weapon: str | None = None,
        damage: str | None = None,
        armor: str | None = None,
    ) -> ResultT[Characters]:
        """Get a single character details based on different parameters.
        Atleast one parameter must be specified. Multiple parameters can be specified
        to get characters based on different filters.

        Keyword Args:
            role: The optional `Role` enum parameter, which gets characters by role.
            type: The optional `type` parameter, which gets characters by the type.
            school: The optional `school` parameter, which gets characters by their school.
            club: The optional `club` parameter, which gets characters by their club.
            position: The optional `Position` enum parameter, which gets characters by their position.
            weapon: The optional `weapon` parameter, which gets characters by their weapon.
            damage: The optional `damage` parameter.
            armor: The optional `armor` parameter.

        Returns:
            [`Result`][barch.Result] containing `Characters` on success or error data on error.

        Raises:
            ValueError: When no arguments are given.

        ??? example

            ```py
            from barch import Client, Role, Position

            client = Client()

            result = await client.character.get_character_by_query(role=Role.Dealer, position=Position.Back)

            if result.is_success:
                characters = result.value

            if result.is_error:
                error = result.error

            await client.close()
        """

        if any([role, type, school, club, position, weapon, damage, armor]):
            params = {
                "role": role.value if role else "",
                "type": type if type else "",
                "school": school if school else "",
                "club": club if club else "",
                "position": position.value if position else "",
                "weapon": weapon if weapon else "",
                "damage": damage if damage else "",
                "armor": armor if armor else "",
            }

            route = endpoints.GET_CHARACTER_QUERY.generate_route().with_params(params)
            result = await self._http.fetch(route)

            if isinstance(result, HttpErrorResponse):
                return Error(result)

            return Success(
                [
                    self._serializer.deserialize_characters_from_query(char)
                    for char in result.data
                ]
            )

        else:
            raise ValueError("Atleast one parameter must be specified.")
