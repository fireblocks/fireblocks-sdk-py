from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class FeePayerInfo(Deserializable):

    def __init__(self, fee_payer_account_id: str) -> None:
        super().__init__()
        self.fee_payer_account_id = fee_payer_account_id

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> FeePayerInfo:
        return cls(
            data.get('feePayerAccountId')
        )
