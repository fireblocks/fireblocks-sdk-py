from __future__ import annotations

from typing import Dict


class ValidateAddressResponse:

    def __init__(self, valid: bool, active: bool, requires_tag: bool) -> None:
        super().__init__()
        self.valid = valid
        self.active = active
        self.requires_tag = requires_tag

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> ValidateAddressResponse:
        return cls(
            data.get('isValid'),
            data.get('isActive'),
            data.get('requiresTag'),
        )
