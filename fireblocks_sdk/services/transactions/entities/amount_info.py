from __future__ import annotations

from typing import Union, Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class AmountInfo(Deserializable):

    def __init__(self, amount: Union[str, None], requested_amount: Union[str, None],
                 net_amount: Union[str, None], amount_usd: Union[str, None]) -> None:
        super().__init__()
        self.amount = amount
        self.requested_amount = requested_amount
        self.net_amount = net_amount
        self.amount_usd = amount_usd

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> AmountInfo:
        return cls(
            data.get('amount'),
            data.get('requestedAmount'),
            data.get('netAmount'),
            data.get('amountUSD')
        )
