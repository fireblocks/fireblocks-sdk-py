from __future__ import annotations

from typing import Dict, List

from fireblocks_sdk.entities.asset_response import AssetResponse


class ExchangeResponse:
    def __init__(self, id: str, type: str, name: str, assets: List[AssetResponse], is_sub_account: bool,
                 status: str) -> None:
        self.id = id
        self.type = type
        self.name = name
        self.assets = assets
        self.is_sub_account = is_sub_account
        self.status = status

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> ExchangeResponse:
        return cls(
            data.get('id'),
            data.get('type'),
            data.get('name'),
            [AssetResponse.deserialize(asset) for asset in data.get('assets')],
            data.get('isSubaccount'),
            data.get('status')
        )
