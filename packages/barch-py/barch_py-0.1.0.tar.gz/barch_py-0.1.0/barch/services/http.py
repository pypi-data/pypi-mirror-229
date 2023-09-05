"""Module for HTTP service."""

from __future__ import annotations
from typing import Any, TypeVar

from barch.models import GenerateRoute, HttpSuccessResponse, HttpErrorResponse

import aiohttp

T = TypeVar("T")

__all__ = ("HttpService",)


class HttpService:
    """The HTTP service that is used to make requets to API."""

    __slots__ = ("_session",)

    def __init__(self) -> None:
        self._session = aiohttp.ClientSession()

    def _get_session_method(self, method: str, session: Any) -> Any:
        """Get the session with method type.

        Returns:
            The session with respective method.
        """

        _method_mapping = {
            "GET": session.get,
            "POST": session.post,
            "PUT": session.put,
            "PATCH": session.patch,
            "DELETE": session.delete,
        }

        return _method_mapping[method]

    async def _request(
        self,
        session: Any,
        uri: str,
        params: dict[str, str | int],
        data: dict[str, str | int],
    ) -> HttpSuccessResponse | HttpErrorResponse:
        """Make the actual request to the MAL API based on given params.

        Returns:
            The response from the API call."""

        try:
            async with session(uri, params=params, data=data) as r:
                response = await r.json()
                if r.status == 200:
                    return HttpSuccessResponse(r.status, "Success.", response)

                return HttpErrorResponse(r.status, response.get("error"))

        except Exception as e:
            return HttpErrorResponse(500, str(e))

    async def fetch(
        self, route: GenerateRoute
    ) -> HttpSuccessResponse | HttpErrorResponse:
        """Makes a request to the given route.

        Returns:
            The HTTP response [`HttpSuccessResponse`] or [`HttpErrorResponse`] of the API call.
        """
        try:
            return await self._request(
                self._get_session_method(route.method, self._session),
                route.uri,
                route.params,
                route.data,
            )

        except Exception as e:
            return HttpErrorResponse(500, str(e))

    async def close(self) -> None:
        """Close the open aiohttp clientsession."""

        if self._session and not self._session.closed:
            await self._session.close()
