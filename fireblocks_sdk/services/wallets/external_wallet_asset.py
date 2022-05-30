from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class ExternalWalletAsset(Deserializable):

    def __init__(self, id: str, status: str, address: str, tag: str, activation_time: str) -> None:
        super().__init__()
        self.id = id
        self.status = status
        self.address = address
        self.tag = tag
        self.activation_time = activation_time

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> ExternalWalletAsset:
        return cls(
            data.get('id'),
            data.get('status'),
            data.get('address'),
            data.get('tag'),
            data.get('activationTime'),
        )


