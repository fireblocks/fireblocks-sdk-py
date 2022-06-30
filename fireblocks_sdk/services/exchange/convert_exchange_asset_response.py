from __future__ import annotations

from typing import Dict


class ConvertExchangeAssetResponse:
    def __init__(self, status: bool) -> None:

        self.status = status

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> ConvertExchangeAssetResponse:
        return cls(
            data.get('status')
        )
