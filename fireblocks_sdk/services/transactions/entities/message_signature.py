from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class MessageSignature(Deserializable):

    def __init__(self, sig: str, r: str, s: str, v: str) -> None:
        super().__init__()
        self.sig = sig
        self.r = r
        self.s = s
        self.v = v

    @classmethod
    def deserialize(cls, data: Dict[str, str]) -> MessageSignature:
        return cls(
            data.get('fullSig'),
            data.get('r'),
            data.get('s'),
            data.get('v')
        )
