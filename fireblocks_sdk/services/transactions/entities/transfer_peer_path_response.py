from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class TransferPeerPathResponse(Deserializable):

    def __init__(self, id: str, type: str, name: str, sub_type: str, virtual_type: str, virtual_id: str) -> None:
        super().__init__()
        self.id = id
        self.type = type
        self.name = name
        self.sub_type = sub_type
        self.virtual_type = virtual_type
        self.virtual_id = virtual_id

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> TransferPeerPathResponse:
        return cls(
            data.get('id'),
            data.get('type'),
            data.get('name'),
            data.get('subType'),
            data.get('virtualType'),
            data.get('virtualId'),
        )
