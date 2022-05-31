from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class EstimatedTransactionFee(Deserializable):

    def __init__(self, network_fee: str, gas_price: str, gas_limit: str, fee_per_byte: str, base_fee: str,
                 priority_fee: str) -> None:
        super().__init__()
        self.network_fee = network_fee
        self.gas_price = gas_price
        self.gas_limit = gas_limit
        self.fee_per_byte = fee_per_byte
        self.base_fee = base_fee
        self.priority_fee = priority_fee

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> EstimatedTransactionFee:
        return cls(
            data.get('networkFee'),
            data.get('gasPrice'),
            data.get('gasLimit'),
            data.get('feePerByte'),
            data.get('baseFee'),
            data.get('priorityFee'),
        )
