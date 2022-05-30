from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable, T


class AmlScreeningResult(Deserializable):

    def __init__(self, provider: str, payload: object, screening_status: str, bypass_reason: str,
                 timestamp: str) -> None:
        super().__init__()
        self.provider = provider
        self.payload = payload
        self.screeningStatus = screening_status
        self.bypass_reason = bypass_reason
        self.timestamp = timestamp

    @classmethod
    def deserialize(cls: T, data: Dict[str, object]) -> AmlScreeningResult:
        return cls(
            data.get('provider'),
            data.get('payload'),
            data.get('screeningStatus'),
            data.get('bypassReason'),
            data.get('timestamp'),
        )
