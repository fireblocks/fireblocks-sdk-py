from __future__ import annotations

from typing import Dict, List

from fireblocks_sdk.entities.deserializable import Deserializable
from fireblocks_sdk.services.fee_payer.fee_info import FeeInfo
from fireblocks_sdk.services.fee_payer.fee_payer_info import FeePayerInfo
from fireblocks_sdk.services.transactions.entities.aml_screening_result import AmlScreeningResult
from fireblocks_sdk.services.transactions.entities.amount_info import AmountInfo
from fireblocks_sdk.services.transactions.entities.authorization_info import AuthorizationInfo
from fireblocks_sdk.services.transactions.entities.block_info import BlockInfo
from fireblocks_sdk.services.transactions.entities.reward_info import RewardInfo
from fireblocks_sdk.services.transactions.entities.signed_message_response import SignedMessageResponse
from fireblocks_sdk.services.transactions.entities.transaction_response_destination import \
    TransactionResponseDestination
from fireblocks_sdk.services.transactions.entities.transfer_peer_path_response import TransferPeerPathResponse


class TransactionResponse(Deserializable):

    def __init__(self, id: str, asset_id: str, source: TransferPeerPathResponse,
                 destination: TransferPeerPathResponse, amount: int,
                 fee: float, network_fee: float, amount_usd: float, net_amount: float,
                 created_at: int, last_updated: int,
                 status: str, tx_hash: str, num_confirmations: int, sub_status: str, signed_by: List[str],
                 created_by: str, rejected_by: str, destination_address: str, destination_address_description: str,
                 destination_tag: str, address_type: str, note: str, exchange_tx_id: str, requested_amount: float,
                 service_fee: float, fee_currency: str, aml_screening_result: AmlScreeningResult, customer_ref_id: str,
                 amount_info: AmountInfo, fee_info: FeeInfo, signed_messages: List[SignedMessageResponse],
                 extra_parameters: object,
                 external_tx_id: str, destinations: List[TransactionResponseDestination], block_info: BlockInfo,
                 authorization_info: AuthorizationInfo, index: int, reward_info: RewardInfo,
                 fee_payer_info: FeePayerInfo) -> None:
        super().__init__()

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> TransactionResponse:
        return cls(
            data.get('id'),
            data.get('assetId'),
            TransferPeerPathResponse.deserialize(data.get('source')),
            TransferPeerPathResponse.deserialize(data.get('destination')),
            data.get('amount'),
            data.get('fee'),
            data.get('networkFee'),
            data.get('amountUSD'),
            data.get('netAmount'),
            data.get('createdAt'),
            data.get('lastUpdated'),
            data.get('status'),
            data.get('txHash'),
            data.get('numOfConfirmations'),
            data.get('subStatus'),
            data.get('signedBy'),
            data.get('createdBy'),
            data.get('rejectedBy'),
            data.get('destinationAddress'),
            data.get('destinationAddressDescription'),
            data.get('destinationTag'),
            data.get('addressType'),
            data.get('note'),
            data.get('exchangeTxId'),
            data.get('requestedAmount'),
            data.get('serviceFee'),
            data.get('feeCurrency'),
            AmlScreeningResult.deserialize(data.get('amlScreeningResult', {})),
            data.get('customerRefId'),
            AmountInfo.deserialize(data.get('amountInfo', {})),
            FeeInfo.deserialize(data.get('feeInfo', {})),
            [SignedMessageResponse.deserialize(message) for message in data.get('signedMessages', [])],
            data.get('extraParameters'),
            data.get('externalTxId'),
            [TransactionResponseDestination.deserialize(destination) for destination in data.get('destinations', [])],
            data.get('blockInfo'),
            AuthorizationInfo.deserialize(data.get('authorizationInfo', {})),
            data.get('index'),
            RewardInfo.deserialize(data.get('rewardInfo', {})),
            FeePayerInfo.deserialize(data.get('feePayerInfo', {})),
        )
