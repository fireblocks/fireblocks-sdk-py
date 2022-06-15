from __future__ import annotations

from typing import Union, Dict


class AssetType:
    def __init__(self, id: str, name: str, type: str, contract_address: str, native_asset: str,
                 decimals: Union[float, None] = None) -> None:
        self.id = id
        self.name = name
        self.type = type
        self.contract_address = contract_address
        self.native_asset = native_asset
        self.decimals = decimals

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> AssetType:
        return cls(data.get("id"), data.get("name"), data.get("type"), data.get("contractAddress"),
                   data.get("nativeAsset"), data.get("decimals", None))
