from __future__ import annotations

from typing import Dict


class NetworkId:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> NetworkId:
        return NetworkId(
            data.get('id'),
            data.get('name'))
