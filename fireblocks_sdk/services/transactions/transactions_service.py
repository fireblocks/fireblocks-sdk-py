import urllib
from typing import Union

from fireblocks_sdk.api_types import FEE_LEVEL, TRANSACTION_STATUS_TYPES, TRANSACTION_TRANSFER, TRANSACTION_TYPES, \
    DestinationTransferPeerPath, FireblocksApiException, TransactionDestination, TransferPeerPath, SIGNING_ALGORITHM, \
    UnsignedMessage
from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.entities.op_success_response import OperationSuccessResponse
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.transactions.entities.create_transaction_response import CreateTransactionResponse
from fireblocks_sdk.services.transactions.entities.estimate_transaction_fee_response import \
    EstimateTransactionFeeResponse
from fireblocks_sdk.services.transactions.entities.page_details import PageDetails
from fireblocks_sdk.services.transactions.entities.transaction_page_response import TransactionPageResponse
from fireblocks_sdk.services.transactions.entities.transaction_response import TransactionResponse
from fireblocks_sdk.services.transactions.entities.validate_address_response import ValidateAddressResponse


class TransactionsService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    def get_transactions_with_page_info(self, before: Union[int, None] = 0, after: Union[int, None] = None,
                                        status: Union[str, None] = None, limit: Union[int, None] = None,
                                        txhash: Union[str, None] = None, assets: Union[str, None] = None,
                                        source_type: Union[str, None] = None, source_id: Union[str, None] = None,
                                        dest_type: Union[str, None] = None, dest_id: Union[str, None] = None,
                                        next_or_previous_path: Union[str, None] = None) -> TransactionPageResponse:
        """Gets a list of transactions matching the given filters or path.
        Note that "next_or_previous_path" is mutually exclusive with other parameters.
        If you wish to iterate over the nextPage/prevPage pages, please provide only the "next_or_previous_path"
        parameter from `pageDetails` response
        example:
            get_transactions_with_page_info(next_or_previous_path=response[pageDetails][nextPage])

        Args:
            before (int, optional): Only gets transactions created before given timestamp (in milliseconds)
            after (int, optional): Only gets transactions created after given timestamp (in milliseconds)
            status (str, optional): Only gets transactions with the specified status, which should one of the following:
                SUBMITTED, QUEUED, PENDING_SIGNATURE, PENDING_AUTHORIZATION, PENDING_3RD_PARTY_MANUAL_APPROVAL,
                PENDING_3RD_PARTY, BROADCASTING, CONFIRMING, COMPLETED, PENDING_AML_CHECKUP, PARTIALLY_COMPLETED,
                CANCELLING, CANCELLED, REJECTED, FAILED, TIMEOUT, BLOCKED
            limit (int, optional): Limit the amount of returned results. If not specified, a limit of 200 results will be used
            txhash (str, optional): Only gets transactions with the specified txHash
            assets (str, optional): Filter results for specified assets
            source_type (str, optional): Only gets transactions with given source_type, which should be one of the following:
                VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, UNKNOWN_PEER, FIAT_ACCOUNT,
                NETWORK_CONNECTION, COMPOUND
            source_id (str, optional): Only gets transactions with given source_id
            dest_type (str, optional): Only gets transactions with given dest_type, which should be one of the following:
                VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, UNKNOWN_PEER, FIAT_ACCOUNT,
                NETWORK_CONNECTION, COMPOUND
            dest_id (str, optional): Only gets transactions with given dest_id
            next_or_previous_path (str, optional): get transactions matching the path, provided from pageDetails
        """
        if next_or_previous_path is not None:
            if not next_or_previous_path:
                return TransactionPageResponse([], PageDetails('', ''))
            index = next_or_previous_path.index('/v1/')
            length = len(next_or_previous_path) - 1
            suffix_path = next_or_previous_path[index:length]

            response = self.connector.get(suffix_path)

            return TransactionPageResponse(
                [TransactionResponse.deserialize(transaction) for transaction in response.content],
                PageDetails(response.extras.get('prevPage'), response.extras.get('nextPage')))
        else:
            return self._get_transactions(before, after, status, limit, None, txhash, assets, source_type, source_id,
                                          dest_type, dest_id)

    def get_transactions(self, before: Union[int, None] = 0, after: Union[int, None] = None,
                         status: Union[str, None] = None, limit: Union[int, None] = None,
                         order_by: Union[str, None] = None, txhash: Union[str, None] = None,
                         assets: Union[str, None] = None,
                         source_type: Union[str, None] = None, source_id: Union[str, None] = None,
                         dest_type: Union[str, None] = None,
                         dest_id: Union[str, None] = None) -> TransactionPageResponse:
        """Gets a list of transactions matching the given filters

        Args:
            before (int, optional): Only gets transactions created before given timestamp (in milliseconds)
            after (int, optional): Only gets transactions created after given timestamp (in milliseconds)
            status (str, optional): Only gets transactions with the specified status, which should one of the following:
                SUBMITTED, QUEUED, PENDING_SIGNATURE, PENDING_AUTHORIZATION, PENDING_3RD_PARTY_MANUAL_APPROVAL,
                PENDING_3RD_PARTY, BROADCASTING, CONFIRMING, COMPLETED, PENDING_AML_CHECKUP, PARTIALLY_COMPLETED,
                CANCELLING, CANCELLED, REJECTED, FAILED, TIMEOUT, BLOCKED
            limit (int, optional): Limit the amount of returned results. If not specified, a limit of 200 results will be used
            order_by (str, optional): Determines the order of the returned results. Possible values are 'createdAt' or 'lastUpdated'
            txhash (str, optional): Only gets transactions with the specified txHash
            assets (str, optional): Filter results for specified assets
            source_type (str, optional): Only gets transactions with given source_type, which should be one of the following:
                VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, UNKNOWN_PEER, FIAT_ACCOUNT,
                NETWORK_CONNECTION, COMPOUND
            source_id (str, optional): Only gets transactions with given source_id
            dest_type (str, optional): Only gets transactions with given dest_type, which should be one of the following:
                VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, UNKNOWN_PEER, FIAT_ACCOUNT,
                NETWORK_CONNECTION, COMPOUND
            dest_id (str, optional): Only gets transactions with given dest_id
        """
        return self._get_transactions(before, after, status, limit, order_by, txhash, assets, source_type, source_id,
                                      dest_type, dest_id)

    def _get_transactions(self, before: Union[int, None] = 0, after: Union[int, None] = None,
                          status: Union[str, None] = None, limit: Union[int, None] = None,
                          order_by: Union[str, None] = None, txhash: Union[str, None] = None,
                          assets: Union[str, None] = None,
                          source_type: Union[str, None] = None, source_id: Union[str, None] = None,
                          dest_type: Union[str, None] = None,
                          dest_id: Union[str, None] = None) -> TransactionPageResponse:
        path = "/v1/transactions"
        params = {}

        if status and status not in TRANSACTION_STATUS_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + status)

        if before:
            params['before'] = before
        if after:
            params['after'] = after
        if status:
            params['status'] = status
        if limit:
            params['limit'] = limit
        if order_by:
            params['orderBy'] = order_by
        if txhash:
            params['txHash'] = txhash
        if assets:
            params['assets'] = assets
        if source_type:
            params['sourceType'] = source_type
        if source_id:
            params['sourceId'] = source_id
        if dest_type:
            params['destType'] = dest_type
        if dest_id:
            params['destId'] = dest_id
        if params:
            path = path + "?" + urllib.parse.urlencode(params)

        response = self.connector.get(path)

        return TransactionPageResponse(
            [TransactionResponse.deserialize(transaction) for transaction in response.content],
            PageDetails(response.extras.get('prevPage'), response.extras.get('nextPage')))

    @response_deserializer(TransactionResponse)
    def get_transaction_by_id(self, tx_id: str) -> TransactionResponse:
        """Gets detailed information for a single transaction

        Args:
            tx_id (str): The transaction id to query
        """

        return self.connector.get(f"/v1/transactions/{tx_id}").content

    @response_deserializer(TransactionResponse)
    def get_transaction_by_external_id(self, external_tx_id) -> TransactionResponse:
        """Gets detailed information for a single transaction

        Args:
            external_tx_id (str): The external id of the transaction
        """

        return self.connector.get(f"/v1/transactions/external_tx_id/{external_tx_id}").content

    @response_deserializer(EstimateTransactionFeeResponse)
    def estimate_fee_for_transaction(self, asset_id, amount, source: TransferPeerPath, destination=None,
                                     tx_type=TRANSACTION_TRANSFER,
                                     idempotency_key=None, destinations=None) -> EstimateTransactionFeeResponse:
        """Estimates transaction fee

        Args:
            asset_id (str): The asset symbol (e.g BTC, ETH)
            source (TransferPeerPath): The transaction source
            destination (DestinationTransferPeerPath, optional): The transfer destination.
            amount (str): The amount
            tx_type (str, optional): Transaction type: either TRANSFER, MINT, BURN, TRANSACTION_SUPPLY_TO_COMPOUND or TRANSACTION_REDEEM_FROM_COMPOUND. Default is TRANSFER.
            idempotency_key (str, optional)
            destinations (list of TransactionDestination objects, optional): For UTXO based assets, send to multiple destinations which should be specified using this field.
        """

        if tx_type not in TRANSACTION_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + tx_type)

        if not isinstance(source, TransferPeerPath):
            raise FireblocksApiException(
                "Expected transaction source of type TransferPeerPath, but got type: " + str(type(source)))

        body = {
            "assetId": asset_id,
            "amount": amount,
            "source": source.__dict__,
            "operation": tx_type
        }

        if destination:
            if not isinstance(destination, (TransferPeerPath, DestinationTransferPeerPath)):
                raise FireblocksApiException(
                    "Expected transaction fee estimation destination of type DestinationTransferPeerPath or TransferPeerPath, but got type: " + type(
                        destination))
            body["destination"] = destination.__dict__

        if destinations:
            if any([not isinstance(x, TransactionDestination) for x in destinations]):
                raise FireblocksApiException(
                    "Expected destinations of type TransactionDestination")
            body['destinations'] = [dest.__dict__ for dest in destinations]

        return self.connector.post("/v1/transactions/estimate_fee", body, idempotency_key).content

    @response_deserializer(OperationSuccessResponse)
    def cancel_transaction_by_id(self, txid, idempotency_key=None) -> OperationSuccessResponse:
        """Cancels the selected transaction

        Args:
            txid (str): The transaction id to cancel
            idempotency_key (str, optional)
        """

        return self.connector.post(f"/v1/transactions/{txid}/cancel", idempotency_key=idempotency_key).content

    def drop_transaction(self, txid, fee_level=None, requested_fee=None, idempotency_key=None):
        """Drops the selected transaction from the blockchain by replacing it with a 0 ETH transaction to itself

        Args:
            txid (str): The transaction id to drop
            fee_level (str): The fee level of the dropping transaction
            requested_fee (str, optional): Requested fee for transaction
            idempotency_key (str, optional)
        """
        body = {}

        if fee_level:
            body["feeLevel"] = fee_level

        if requested_fee:
            body["requestedFee"] = requested_fee

        return self.connector.post(f"/v1/transactions/{txid}/drop", body, idempotency_key)

    @response_deserializer(OperationSuccessResponse)
    def freeze_transaction_by_id(self, txId, idempotency_key=None) -> OperationSuccessResponse:
        """Freezes the selected transaction

        Args:
            txId (str): The transaction ID to freeze
            idempotency_key (str, optional)
        """
        return self.connector.post(f"/v1/transactions/{txId}/freeze", idempotency_key=idempotency_key).content

    @response_deserializer(OperationSuccessResponse)
    def unfreeze_transaction_by_id(self, txId, idempotency_key=None) -> OperationSuccessResponse:
        """Unfreezes the selected transaction

        Args:
            txId (str): The transaction ID to unfreeze
            idempotency_key (str, optional)
        """
        return self.connector.post(f"/v1/transactions/{txId}/unfreeze", idempotency_key=idempotency_key).content

    @response_deserializer(CreateTransactionResponse)
    def create_transaction(self, asset_id=None, amount=None, source=None, destination=None, fee=None, gas_price=None,
                           wait_for_status=False, tx_type=TRANSACTION_TRANSFER, note=None, network_fee=None,
                           customer_ref_id=None, replace_tx_by_hash=None, extra_parameters=None, destinations=None,
                           fee_level=None, fail_on_low_fee=None, max_fee=None, gas_limit=None, idempotency_key=None,
                           external_tx_id=None, treat_as_gross_amount=None,
                           force_sweep=None) -> CreateTransactionResponse:
        """Creates a new transaction

        Args:
            asset_id (str, optional): The asset symbol (e.g BTC, ETH)
            source (TransferPeerPath, optional): The transfer source
            destination (DestinationTransferPeerPath, optional): The transfer destination. Leave empty (None) if the transaction has no destination
            amount (double): The amount
            fee (double, optional): Sathoshi/Latoshi per byte.
            gas_price (number, optional): gasPrice for ETH and ERC-20 transactions.
            wait_for_status (bool, optional): If true, waits for transaction status. Default is false.
            tx_type (str, optional): Transaction type: either TRANSFER, MINT, BURN, TRANSACTION_SUPPLY_TO_COMPOUND or TRANSACTION_REDEEM_FROM_COMPOUND. Default is TRANSFER.
            note (str, optional): A custome note that can be associated with the transaction.
            network_fee (str, optional): Transaction blockchain fee (For Ethereum, you can't pass gasPrice, gasLimit and networkFee all together)
            customer_ref_id (string, optional): The ID for AML providers to associate the owner of funds with transactions
            extra_parameters (object, optional)
            destinations (list of TransactionDestination objects, optional): For UTXO based assets, send to multiple destinations which should be specified using this field.
            fee_level (FeeLevel, optional): Transaction fee level: either HIGH, MEDIUM, LOW.
            fail_on_low_fee (bool, optional): False by default, if set to true and MEDIUM fee level is higher than the one specified in the transaction, the transction will fail.
            max_fee (str, optional): The maximum fee (gas price or fee per byte) that should be payed for the transaction.
            gas_limit (number, optional): For ETH-based assets only.
            idempotency_key (str, optional)
            external_tx_id (str, optional): A unique key for transaction provided externally
            treat_as_gross_amount (bool, optional): Determine if amount should be treated as gross or net
            force_sweep (bool, optional): Determine if transaction should be treated as a forced sweep
        """

        if tx_type not in TRANSACTION_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + tx_type)

        if source:
            if not isinstance(source, TransferPeerPath):
                raise FireblocksApiException(
                    "Expected transaction source of type TransferPeerPath, but got type: " + type(source))

        body = {
            "waitForStatus": wait_for_status,
            "operation": tx_type,
        }

        if asset_id:
            body["assetId"] = asset_id

        if source:
            body["source"] = source.__dict__

        if amount is not None:
            body["amount"] = amount

        if fee:
            body["fee"] = fee

        if fee_level:
            if fee_level not in FEE_LEVEL:
                raise FireblocksApiException("Got invalid fee level: " + fee_level)
            body["feeLevel"] = fee_level

        if max_fee:
            body["maxFee"] = max_fee

        if fail_on_low_fee:
            body["failOnLowFee"] = fail_on_low_fee

        if gas_price:
            body["gasPrice"] = str(gas_price)

        if gas_limit:
            body["gasLimit"] = str(gas_limit)

        if note:
            body["note"] = note

        if destination:
            if not isinstance(destination, (TransferPeerPath, DestinationTransferPeerPath)):
                raise FireblocksApiException(
                    "Expected transaction destination of type DestinationTransferPeerPath or TransferPeerPath, but got type: " + type(
                        destination))
            body["destination"] = destination.__dict__

        if network_fee:
            body["networkFee"] = network_fee

        if customer_ref_id:
            body["customerRefId"] = customer_ref_id

        if replace_tx_by_hash:
            body["replaceTxByHash"] = replace_tx_by_hash

        if treat_as_gross_amount:
            body["treatAsGrossAmount"] = treat_as_gross_amount

        if destinations:
            if any([not isinstance(x, TransactionDestination) for x in destinations]):
                raise FireblocksApiException("Expected destinations of type TransactionDestination")

            body['destinations'] = [dest.__dict__ for dest in destinations]

        if extra_parameters:
            body["extraParameters"] = extra_parameters

        if external_tx_id:
            body["externalTxId"] = external_tx_id

        if force_sweep:
            body["forceSweep"] = force_sweep

        return self.connector.post("/v1/transactions", body, idempotency_key).content

    @response_deserializer(OperationSuccessResponse)
    def set_confirmation_threshold_for_txid(self, txid, required_confirmations_number,
                                            idempotency_key=None) -> OperationSuccessResponse:
        """Set the required number of confirmations for transaction

        Args:
            txid (str): The transaction id
            required_confirmations_Number (number): Required confirmation threshold fot the txid
            idempotency_key (str, optional)
        """

        body = {
            "numOfConfirmations": required_confirmations_number
        }

        return self.connector.post(f"/v1/transactions/{txid}/set_confirmation_threshold", body, idempotency_key).content

    @response_deserializer(ValidateAddressResponse)
    def validate_address(self, asset_id, address) -> ValidateAddressResponse:
        """Gets vault accumulated balance by asset

        Args:
            asset_id (str): The asset symbol (e.g XRP, EOS)
            address (str): The address to be verified
        """
        url = f"/v1/transactions/validate_address/{asset_id}/{address}"

        return self.connector.get(url).content

    def create_raw_transaction(self, raw_message, source=None, asset_id=None, note=None) -> CreateTransactionResponse:
        """Creates a new raw transaction with the specified parameters

        Args:
            raw_message (RawMessage): The messages that should be signed
            source (TransferPeerPath, optional): The transaction source
            asset_id (str, optional): Transaction asset id
            note (str, optional): A custome note that can be associated with the transaction
        """

        if asset_id is None:
            if raw_message.algorithm not in SIGNING_ALGORITHM:
                raise Exception("Got invalid signing algorithm type: " + raw_message.algorithm)

        if not all([isinstance(x, UnsignedMessage) for x in raw_message.messages]):
            raise FireblocksApiException("Expected messages of type UnsignedMessage")

        raw_message.messages = [message.__dict__ for message in raw_message.messages]

        return self.create_transaction(asset_id, source=source, tx_type="RAW",
                                       extra_parameters={"rawMessageData": raw_message.__dict__}, note=note)
