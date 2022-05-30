from __future__ import annotations

from typing import List, Dict

from fireblocks_sdk.entities.deserializable import Deserializable, T
from fireblocks_sdk.services.transactions.entities.page_details import PageDetails
from fireblocks_sdk.services.transactions.entities.transaction_response import TransactionResponse


class TransactionPageResponse(Deserializable):

    def __init__(self, transactions: List[TransactionResponse], page_details: PageDetails) -> None:
        super().__init__()
        self.transactions = transactions
        self.page_details = page_details

    @classmethod
    def deserialize(cls: T, data: Dict[str, any]) -> TransactionPageResponse:
        return cls(
            [TransactionResponse.deserialize(transaction) for transaction in data.get('transactions')],
            PageDetails.deserialize(data.get('pageDetails'))
        )
