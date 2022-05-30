from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable, T


class PageDetails(Deserializable):

    def __init__(self, prev_page: str, next_page: str) -> None:
        super().__init__()
        self.prev_page = prev_page
        self.next_page = next_page

    @classmethod
    def deserialize(cls: T, data: Dict[str, str]) -> PageDetails:
        return cls(
            data.get('prevPage'),
            data.get('nextPage')
        )
