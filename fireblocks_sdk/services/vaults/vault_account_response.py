from __future__ import annotations

from typing import Dict, List, Union

from fireblocks_sdk.entities.asset_response import AssetResponse
from fireblocks_sdk.entities.deserializable import Deserializable


class VaultAccountResponse(Deserializable):
    def __init__(self, id: str, name: str, hidden_on_ui: bool, assets: List[AssetResponse], auto_fuel: bool,
                 customer_ref_id: Union[str, None]) -> None:
        self.id = id
        self.name = name
        self.hidden_on_ui = hidden_on_ui
        self.assets = assets
        self.auto_fuel = auto_fuel
        self.customerRefId = customer_ref_id

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> VaultAccountResponse:
        print('deserializing....')
        assets = [AssetResponse.deserialize(asset) for asset in data.get('assets')]
        return cls(data.get('id'),
                   data.get('name'),
                   data.get('hiddenOnUI'),
                   assets,
                   data.get('autoFuel'),
                   data.get('customerRefId'))
