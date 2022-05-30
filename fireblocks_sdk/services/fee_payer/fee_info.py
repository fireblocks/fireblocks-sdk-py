from __future__ import annotations

from typing import Dict, Union

from fireblocks_sdk.entities.deserializable import Deserializable


class FeeInfo(Deserializable):

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> FeeInfo:
        return cls(
            data.get('networkFee'),
            data.get('serviceFee'),
            data.get('gasPrice'),
        )

    def __init__(self, network_fee: Union[str, None], service_fee: Union[str, None],
                 gas_price: Union[str, None]) -> None:
        super().__init__()
        self.network_fee = network_fee
        self.service_fee = service_fee
        self.gas_price = gas_price
