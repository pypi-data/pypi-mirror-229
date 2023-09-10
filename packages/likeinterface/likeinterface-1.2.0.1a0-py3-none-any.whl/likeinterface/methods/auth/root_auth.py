from __future__ import annotations

from typing import TYPE_CHECKING

from likeinterface.methods.base import Method, Request

if TYPE_CHECKING:
    from likeinterface.interface import Interface


class RootAuthMethod(Method[bool]):
    """
    Use this method to get service health.

    Parameters
      This constructor does not require any parameters.

    Result
      :class:`bool`
    """

    __name__ = "auth"
    __returning__ = bool

    def request(self, interface: Interface) -> Request:
        return Request(method=self.__name__, data=self.model_dump())
