from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class FeePayerConfiguration(Deserializable):

    def __init__(self, fee_payer_account_id: str) -> None:
        super().__init__()
        self.fee_payer_accountId = fee_payer_account_id

    @classmethod
    def deserialize(cls, data: Dict[str, str]) -> FeePayerConfiguration:
        return cls(
            data.get('feePayerAccountId')
        )
