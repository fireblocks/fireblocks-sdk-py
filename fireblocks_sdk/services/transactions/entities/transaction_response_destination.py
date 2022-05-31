from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable
from fireblocks_sdk.services.transactions.entities.aml_screening_result import AmlScreeningResult
from fireblocks_sdk.services.transactions.entities.authorization_info import AuthorizationInfo
from fireblocks_sdk.services.transactions.entities.transfer_peer_path_response import TransferPeerPathResponse


class TransactionResponseDestination(Deserializable):

    def __init__(self, amount: str, amount_usd: str,
                 aml_screening_result: AmlScreeningResult, destination: TransferPeerPathResponse,
                 authorization_info: AuthorizationInfo) -> None:
        super().__init__()
        self.amount = amount
        self.amount_usd = amount_usd
        self.aml_screening_result = aml_screening_result
        self.destination = destination
        self.authorization_info = authorization_info

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> TransactionResponseDestination:
        return cls(
            data.get('amount'),
            data.get('amountUSD'),
            AmlScreeningResult.deserialize(data.get('amlScreeningResult')),
            TransferPeerPathResponse.deserialize(data.get('destination')),
            AuthorizationInfo.deserialize(data.get('authorizationInfo'))
        )
