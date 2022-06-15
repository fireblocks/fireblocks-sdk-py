from __future__ import annotations

from typing import Dict, List, Union

from fireblocks_sdk.entities.asset_response import AssetResponse


class FiatAccountResponse:
    def __init__(self, id: str, type: str, name: str, assets: List[AssetResponse], address: Union[str, None]) -> None:
        self.id = id
        self.type = type
        self.name = name
        self.assets = assets
        self.address = address

    @classmethod
    def deserialize(cls, data: Dict[str, str]) -> FiatAccountResponse:
        return FiatAccountResponse(
            data.get('id'),
            data.get('type'),
            data.get('name'),
            [AssetResponse.deserialize(asset) for asset in data.get('assets')],
            data.get('address'),
        )
