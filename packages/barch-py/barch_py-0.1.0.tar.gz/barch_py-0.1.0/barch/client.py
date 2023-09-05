"""This module has the client to connect to BlueArchive API."""

from __future__ import annotations
from barch import services, serializer

__all__ = ("Client",)


class Client:
    """An asynchronous client used to interact with the BlueArchive API."""

    __slots__ = ("_http", "_serializer", "_character", "_raid")

    def __init__(self) -> None:
        self._http = services.HttpService()
        self._serializer = serializer.Serializer()
        self._character = services.CharacterService(self._http, self._serializer)
        self._raid = services.RaidService(self._http, self._serializer)

    @property
    def character(self) -> services.CharacterService:
        """The [`CharacterService`][barch.CharacterService] used to make character related requests."""

        return self._character

    @property
    def raid(self) -> services.RaidService:
        """The [`RaidService`][barch.RaidService] used to make raid related requests."""

        return self._raid

    async def close(self) -> None:
        """Close the existing client session.

        !!! warning

            You will receive an error in your console if this is not called before the program terminates."""
        
        await self._http.close()
