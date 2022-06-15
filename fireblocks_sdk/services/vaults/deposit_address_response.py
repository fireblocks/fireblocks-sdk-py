from __future__ import annotations

from ctypes import Union
from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class DepositAddressResponse(Deserializable):
    def __init__(self, asset_id: str, address: str, address_format: str,
                 legacy_address: Union[str, None], enterprise_address: Union[str, None], type: str,
                 tag: Union[str, None], description: Union[str, None], customer_ref_id: Union[str, None]) -> None:
        self.asset_id = asset_id
        self.address = address
        self.address_format = address_format
        self.legacy_address = legacy_address
        self.enterprise_address = enterprise_address
        self.type = type
        self.tag = tag
        self.description = description
        self.customer_ref_id = customer_ref_id

    @classmethod
    def deserialize(cls, data: Dict[str]) -> DepositAddressResponse:
        return cls(
            data.get('assetId'),
            data.get('address'),
            data.get('tag'),
            data.get('description'),
            data.get('type'),
            data.get('customerRefId'),
            data.get('addressFormat'),
            data.get('legacyAddress'),
            data.get('enterpriseAddress')
        )
