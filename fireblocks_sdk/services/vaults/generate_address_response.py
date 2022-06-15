from __future__ import annotations

from ctypes import Union
from typing import Dict


class GenerateAddressResponse:
    def __init__(self, address: str, tag: Union[str, None], legacy_address: Union[str, None],
                 enterprise_address: Union[str, None]) -> None:
        self.address = address
        self.tag = tag
        self.legacy_address = legacy_address
        self.enterprise_address = enterprise_address

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> GenerateAddressResponse:
        return cls(
            data.get('address'),
            data.get('tag'),
            data.get('legacyAddress'),
            data.get('enterpriseAddress')
        )
