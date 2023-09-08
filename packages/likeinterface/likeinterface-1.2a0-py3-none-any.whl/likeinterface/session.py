from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional, cast

from aiohttp.client import ClientError, ClientSession

from likeinterface.exceptions import LikeNetworkError
from likeinterface.methods import LikeType, Method
from likeinterface.utils.response_validator import response_validator

if TYPE_CHECKING:
    from likeinterface.interface import Interface


class SessionManager:
    def __init__(
        self,
        session: Optional[ClientSession] = None,
        *,
        connect_kwargs: Dict[str, Any] = defaultdict(),  # noqa
    ) -> None:
        self.session = session
        self.connect_kwargs = connect_kwargs
        self.should_reset_connector = not self.session

    async def create(self) -> None:
        if self.should_reset_connector:
            await self.close()
        if self.session is None or self.session.closed:
            self.session = ClientSession(**self.connect_kwargs)
            self.should_reset_connector = False

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()


class Session(SessionManager):
    def __init__(
        self,
        *,
        session: Optional[ClientSession] = None,
        connect_kwargs: Dict[str, Any] = defaultdict(),  # noqa
    ) -> None:
        super(Session, self).__init__(
            session=session,
            connect_kwargs=connect_kwargs,
        )

    async def request(
        self, interface: Interface, method: Method[LikeType], timeout: int = 60
    ) -> LikeType:
        await self.create()

        request = method.request(interface=interface)

        try:
            async with self.session.post(
                url=interface.network.url(method=method.__name__),
                json=request.data,
                timeout=timeout,
            ) as response:
                content = await response.text()
        except asyncio.TimeoutError:
            raise LikeNetworkError("Exception %s: %s." % (method, "request timeout error"))
        except ClientError as e:
            raise LikeNetworkError(
                "Exception for method %s: %s." % (method.__name__, f"{type(e).__name__}: {e}")
            )

        response = response_validator(method=method, status_code=response.status, content=content)
        return cast(LikeType, response.result)

    async def stream(
        self,
        interface: Interface,
        file: str,
        timeout: int = 60,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        await self.create()

        async with self.session.post(
            url=interface.network.file(file=file),
            timeout=timeout,
            raise_for_status=raise_for_status,
        ) as response:
            async for chunk in response.content.iter_chunked(chunk_size):
                yield chunk
