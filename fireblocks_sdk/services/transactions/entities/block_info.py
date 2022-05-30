from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class BlockInfo(Deserializable):

    def __init__(self, block_height: str, block_hash: str) -> None:
        super().__init__()
        self.block_height = block_height
        self.block_hash = block_hash

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> BlockInfo:
        return cls(
            data.get('blockHeight'),
            data.get('blockHash')
        )
