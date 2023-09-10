from __future__ import annotations

from typing import Any

from pydantic.dataclasses import dataclass


@dataclass
class Network:
    """
    Class describing access to different services.
    """

    base: str
    file_base: str

    def url(self, **kwargs: Any) -> str:
        """
        Formats base url for request.

        :param kwargs: format kwargs
        :return: url
        """

        return self.base.format(**kwargs)

    def file(self, **kwargs: Any) -> str:
        """
        Formats base url for file.

        :param kwargs: format kwargs
        :return: url
        """

        return self.file_base.format(**kwargs)
