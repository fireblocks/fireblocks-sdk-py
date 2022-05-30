from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable
from fireblocks_sdk.services.transactions.entities.message_signature import MessageSignature


class SignedMessageResponse(Deserializable):

    def __init__(self, content: str, algorithm: str, derivation_path: str, signature: MessageSignature,
                 public_key: str) -> None:
        super().__init__()
        self.content = content
        self.algorithm = algorithm
        self.derivation_path = derivation_path
        self.signature = signature
        self.public_key = public_key

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> SignedMessageResponse:
        return cls(
            data.get('content'),
            data.get('algorithm'),
            data.get('derivationPath'),
            MessageSignature.deserialize(data.get('signature')),
            data.get('publicKey'),
        )
