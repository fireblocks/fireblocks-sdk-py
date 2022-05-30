from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable
from fireblocks_sdk.services.transactions.entities.estimated_transaction_fee import EstimatedTransactionFee


class EstimateTransactionFeeResponse(Deserializable):

    def __init__(self, low: EstimatedTransactionFee, medium: EstimatedTransactionFee,
                 high: EstimatedTransactionFee) -> None:
        super().__init__()
        self.low = low
        self.medium = medium
        self.high = high

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> EstimateTransactionFeeResponse:
        return cls(
            EstimatedTransactionFee.deserialize(data.get('low')),
            EstimatedTransactionFee.deserialize(data.get('medium')),
            EstimatedTransactionFee.deserialize(data.get('high'))
        )
