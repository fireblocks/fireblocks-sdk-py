from operator import attrgetter

import requests
import urllib
import json

from .sdk_token_provider import SdkTokenProvider
from .api_types import FireblocksApiException, TRANSACTION_TYPES, TRANSACTION_STATUS_TYPES, PEER_TYPES, \
    TransferPeerPath, DestinationTransferPeerPath, TransferTicketTerm, TRANSACTION_TRANSFER, SIGNING_ALGORITHM, \
    UnsignedMessage, FEE_LEVEL, PagedVaultAccountsRequestFilters
from fireblocks_sdk.api_types import TransactionDestination


def handle_response(response, page_mode=False):
    try:
        response_data = response.json()
    except:
        response_data = None
    if response.status_code >= 300:
        if type(response_data) is dict:
            error_code = response_data.get("code")
            raise FireblocksApiException("Got an error from fireblocks server: " + response.text, error_code)
        else:
            raise FireblocksApiException("Got an error from fireblocks server: " + response.text)
    else:
        if page_mode:
            return {'transactions': response_data,
                    'pageDetails': {'prevPage': response.headers.get('prev-page', ''),
                                    'nextPage': response.headers.get('next-page', '')}}
        return response_data


class FireblocksSDK(object):

    def __init__(self, private_key, api_key, api_base_url="https://api.fireblocks.io", timeout=None):
        """Creates a new Fireblocks API Client.

        Args:
            private_key (str): A string representation of your private key (in PEM format)
            api_key (str): Your api key. This is a uuid you received from Fireblocks
            base_url (str): The fireblocks server URL. Leave empty to use the default server
            timeout (number): Timeout for http requests in seconds
        """
        self.private_key = private_key
        self.api_key = api_key
        self.base_url = api_base_url
        self.token_provider = SdkTokenProvider(private_key, api_key)
        self.timeout = timeout

    def get_supported_assets(self):
        """Gets all assets that are currently supported by Fireblocks"""

        return self._get_request("/v1/supported_assets")

    def get_vault_accounts(self, name_prefix=None, name_suffix=None, min_amount_threshold=None, assetId=None):
        """Gets all vault accounts for your tenant

        Args:
            name_prefix (string, optional): Vault account name prefix
            name_suffix (string, optional): Vault account name suffix
            min_amount_threshold (number, optional):  The minimum amount for asset to have in order to be included in the results
            assetId (string, optional): The asset symbol
        """

        url = f"/v1/vault/accounts"

        params = {}

        if name_prefix:
            params['namePrefix'] = name_prefix

        if name_suffix:
            params['nameSuffix'] = name_suffix

        if min_amount_threshold is not None:
            params['minAmountThreshold'] = min_amount_threshold

        if assetId is not None:
            params['assetId'] = assetId

        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        return self._get_request(url)

    def get_vault_accounts_with_page_info(self, paged_vault_accounts_request_filters: PagedVaultAccountsRequestFilters):
        """Gets a page of vault accounts for your tenant according to filters given

        Args:
            paged_vault_accounts_request_filters (object, optional): Possible filters to apply for request
        """

        url = f"/v1/vault/accounts_paged"
        name_prefix, name_suffix, min_amount_threshold, asset_id, order_by, limit, before, after = \
            attrgetter('name_prefix', 'name_suffix', 'min_amount_threshold', 'asset_id', 'order_by', 'limit', 'before', 'after')(paged_vault_accounts_request_filters)

        params = {}

        if name_prefix:
            params['namePrefix'] = name_prefix

        if name_suffix:
            params['nameSuffix'] = name_suffix

        if min_amount_threshold is not None:
            params['minAmountThreshold'] = min_amount_threshold

        if asset_id is not None:
            params['assetId'] = asset_id

        if order_by is not None:
            params['orderBy'] = order_by

        if limit is not None:
            params['limit'] = limit

        if before is not None:
            params['before'] = before

        if after is not None:
            params['after'] = after

        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        return self._get_request(url)

    def get_vault_account(self, vault_account_id):
        """Deprecated - Replaced by get_vault_account_by_id
        Args:
            vault_account_id (string): The id of the requested account
        """

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}")

    def get_vault_account_by_id(self, vault_account_id):
        """Gets a single vault account
        Args:
            vault_account_id (string): The id of the requested account
        """

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}")

    def get_vault_account_asset(self, vault_account_id, asset_id):
        """Gets a single vault account asset
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}")

    def refresh_vault_asset_balance(self, vault_account_id, asset_id, idempotency_key=None):
        """Gets a single vault account asset after forcing refresh from the blockchain
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/balance", {}, idempotency_key)

    def get_deposit_addresses(self, vault_account_id, asset_id):
        """Gets deposit addresses for an asset in a vault account
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses")

    def get_unspent_inputs(self, vault_account_id, asset_id):
        """Gets utxo list for an asset in a vault account
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (like BTC, DASH and utxo based assets)
        """

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/unspent_inputs")

    def generate_new_address(self, vault_account_id, asset_id, description=None, customer_ref_id=None,
                             idempotency_key=None):
        """Generates a new address for an asset in a vault account

        Args:
            vault_account_id (string): The vault account ID
            asset_id (string): The ID of the asset for which to generate the deposit address
            description (string, optional): A description for the new address
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses",
                                  {"description": description or '', "customerRefId": customer_ref_id or ''},
                                  idempotency_key)

    def set_address_description(self, vault_account_id, asset_id, address, tag=None, description=None):
        """Sets the description of an existing address

        Args:
            vault_account_id (string): The vault account ID
            asset_id (string): The ID of the asset
            address (string): The address for which to set the set_address_description
            tag (string, optional): The XRP tag, or EOS memo, for which to set the description
            description (string, optional): The description to set, or none for no description
        """
        if tag:
            return self._put_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}:{tag}",
                                     {"description": description or ''})
        else:
            return self._put_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}",
                                     {"description": description or ''})

    def get_network_connections(self):
        """Gets all network connections for your tenant"""

        return self._get_request("/v1/network_connections")

    def get_network_connection_by_id(self, connection_id):
        """Gets a single network connection by id
        Args:
            connection_id (string): The ID of the network connection
        """

        return self._get_request(f"/v1/network_connections/{connection_id}")

    def get_exchange_accounts(self):
        """Gets all exchange accounts for your tenant"""

        return self._get_request("/v1/exchange_accounts")

    def get_exchange_account(self, exchange_account_id):
        """Gets an exchange account for your tenant
        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
        """

        return self._get_request(f"/v1/exchange_accounts/{exchange_account_id}")

    def get_exchange_account_asset(self, exchange_account_id, asset_id):
        """Get a specific asset from an exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            asset_id (string): The asset to transfer
        """

        return self._get_request(f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}")

    def transfer_to_subaccount(self, exchange_account_id, subaccount_id, asset_id, amount, idempotency_key=None):
        """Transfer to a subaccount from a main exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            subaccount_id (string): The ID of the subaccount in the exchange
            asset_id (string): The asset to transfer
            amount (double): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {
            "subaccountId": subaccount_id,
            "amount": amount
        }

        return self._post_request(f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}/transfer_to_subaccount",
                                  body, idempotency_key)

    def transfer_from_subaccount(self, exchange_account_id, subaccount_id, asset_id, amount, idempotency_key=None):
        """Transfer from a subaccount to a main exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            subaccount_id (string): The ID of the subaccount in the exchange
            asset_id (string): The asset to transfer
            amount (double): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {
            "subaccountId": subaccount_id,
            "amount": amount
        }

        return self._post_request(f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}/transfer_from_subaccount",
                                  body, idempotency_key)

    def get_fiat_accounts(self):
        """Gets all fiat accounts for your tenant"""

        return self._get_request("/v1/fiat_accounts")

    def get_fiat_account_by_id(self, account_id):
        """Gets a single fiat account by ID

        Args:
            account_id (string): The fiat account ID
        """

        return self._get_request(f"/v1/fiat_accounts/{account_id}")

    def redeem_to_linked_dda(self, account_id, amount, idempotency_key=None):
        """Redeem from a fiat account to a linked DDA

        Args:
            account_id (string): The fiat account ID in Fireblocks
            amount (double): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {
            "amount": amount,
        }

        return self._post_request(f"/v1/fiat_accounts/{account_id}/redeem_to_linked_dda", body, idempotency_key)

    def deposit_from_linked_dda(self, account_id, amount, idempotency_key=None):
        """Deposit to a fiat account from a linked DDA

        Args:
            account_id (string): The fiat account ID in Fireblocks
            amount (double): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {
            "amount": amount,
        }

        return self._post_request(f"/v1/fiat_accounts/{account_id}/deposit_from_linked_dda", body, idempotency_key)

    def get_transactions_with_page_info(self, before=0, after=None, status=None, limit=None, txhash=None,
                                        assets=None, source_type=None, source_id=None, dest_type=None, dest_id=None,
                                        next_or_previous_path=None):
        """Gets a list of transactions matching the given filters or path.
        Note that "next_or_previous_path" is mutually exclusive with other parameters.
        If you wish to iterate over the nextPage/prevPage pages, please provide only the "next_or_previous_path" parameter from `pageDetails` response
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
                return {'transactions': [], 'pageDetails': {'prevPage': '', 'nextPage': ''}}
            index = next_or_previous_path.index('/v1/')
            length = len(next_or_previous_path) - 1
            suffix_path = next_or_previous_path[index:length]
            return self._get_request(suffix_path, True)
        else:
            return self._get_transactions(before, after, status, limit, None, txhash, assets, source_type, source_id,
                                          dest_type, dest_id, True)

    def get_transactions(self, before=0, after=0, status=None, limit=None, order_by=None, txhash=None,
                         assets=None, source_type=None, source_id=None, dest_type=None, dest_id=None):
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

    def _get_transactions(self, before, after, status, limit, order_by, txhash, assets, source_type, source_id,
                          dest_type, dest_id, page_mode=False):
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

        return self._get_request(path, page_mode)

    def get_internal_wallets(self):
        """Gets all internal wallets for your tenant"""

        return self._get_request("/v1/internal_wallets")

    def get_internal_wallet(self, wallet_id):
        """Gets an internal wallet from your tenant
        Args:
            wallet_id (str): The wallet id to query
        """

        return self._get_request(f"/v1/internal_wallets/{wallet_id}")

    def get_internal_wallet_asset(self, wallet_id, asset_id):
        """Gets an asset from an internal wallet from your tenant
        Args:
            wallet_id (str): The wallet id to query
            asset_id (str): The asset id to query
        """
        return self._get_request(f"/v1/internal_wallets/{wallet_id}/{asset_id}")

    def get_external_wallets(self):
        """Gets all external wallets for your tenant"""

        return self._get_request("/v1/external_wallets")

    def get_external_wallet(self, wallet_id):
        """Gets an external wallet from your tenant
        Args:
            wallet_id (str): The wallet id to query
        """

        return self._get_request(f"/v1/external_wallets/{wallet_id}")

    def get_external_wallet_asset(self, wallet_id, asset_id):
        """Gets an asset from an external wallet from your tenant
        Args:
            wallet_id (str): The wallet id to query
            asset_id (str): The asset id to query
        """
        return self._get_request(f"/v1/external_wallets/{wallet_id}/{asset_id}")

    def get_transaction_by_id(self, txid):
        """Gets detailed information for a single transaction

        Args:
            txid (str): The transaction id to query
        """

        return self._get_request(f"/v1/transactions/{txid}")

    def get_transaction_by_external_id(self, external_tx_id):
        """Gets detailed information for a single transaction

        Args:
            external_tx_id (str): The external id of the transaction
        """

        return self._get_request(f"/v1/transactions/external_tx_id/{external_tx_id}")

    def get_fee_for_asset(self, asset_id):
        """Gets the estimated fees for an asset

        Args:
            asset_id (str): The asset symbol (e.g BTC, ETH)
        """

        return self._get_request(f"/v1/estimate_network_fee?assetId={asset_id}")

    def estimate_fee_for_transaction(self, asset_id, amount, source, destination=None, tx_type=TRANSACTION_TRANSFER,
                                     idempotency_key=None, destinations=None):
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
                "Expected transaction source of type TransferPeerPath, but got type: " + type(source))

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
                raise FireblocksApiException("Expected destinations of type TransactionDestination")
            body['destinations'] = [dest.__dict__ for dest in destinations]

        return self._post_request("/v1/transactions/estimate_fee", body, idempotency_key)

    def cancel_transaction_by_id(self, txid, idempotency_key=None):
        """Cancels the selected transaction

        Args:
            txid (str): The transaction id to cancel
            idempotency_key (str, optional)
        """

        return self._post_request(f"/v1/transactions/{txid}/cancel", idempotency_key=idempotency_key)

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

        return self._post_request(f"/v1/transactions/{txid}/drop", body, idempotency_key)

    def create_vault_account(self, name, hiddenOnUI=False, customer_ref_id=None, autoFuel=False, idempotency_key=None):
        """Creates a new vault account.

        Args:
            name (str): A name for the new vault account
            hiddenOnUI (boolean): Specifies whether the vault account is hidden from the web console, false by default
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """
        body = {
            "name": name,
            "hiddenOnUI": hiddenOnUI,
            "autoFuel": autoFuel
        }

        if customer_ref_id:
            body["customerRefId"] = customer_ref_id

        return self._post_request("/v1/vault/accounts", body, idempotency_key)

    def hide_vault_account(self, vault_account_id, idempotency_key=None):
        """Hides the vault account from being visible in the web console

        Args:
            vault_account_id (str): The vault account Id
            idempotency_key (str, optional)
        """
        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/hide", idempotency_key=idempotency_key)

    def unhide_vault_account(self, vault_account_id, idempotency_key=None):
        """Returns the vault account to being visible in the web console

        Args:
            vault_account_id (str): The vault account Id
            idempotency_key (str, optional)
        """
        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/unhide", idempotency_key=idempotency_key)

    def freeze_transaction_by_id(self, txId, idempotency_key=None):
        """Freezes the selected transaction

        Args:
            txId (str): The transaction ID to freeze
            idempotency_key (str, optional)
        """
        return self._post_request(f"/v1/transactions/{txId}/freeze", idempotency_key=idempotency_key)

    def unfreeze_transaction_by_id(self, txId, idempotency_key=None):
        """Unfreezes the selected transaction

        Args:
            txId (str): The transaction ID to unfreeze
            idempotency_key (str, optional)
        """
        return self._post_request(f"/v1/transactions/{txId}/unfreeze", idempotency_key=idempotency_key)

    def update_vault_account(self, vault_account_id, name):
        """Updates a vault account.

        Args:
            vault_account_id (str): The vault account Id
            name (str): A new name for the vault account
        """
        body = {
            "name": name,
        }

        return self._put_request(f"/v1/vault/accounts/{vault_account_id}", body)

    def create_vault_asset(self, vault_account_id, asset_id, idempotency_key=None):
        """Creates a new asset within an existing vault account

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            idempotency_key (str, optional)
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}", idempotency_key=idempotency_key)

    def activate_vault_asset(self, vault_account_id, asset_id, idempotency_key=None):
        """Retry to create a vault asset for a vault asset that failed

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            idempotency_key (str, optional)
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/activate",
                                  idempotency_key=idempotency_key)

    def set_vault_account_customer_ref_id(self, vault_account_id, customer_ref_id, idempotency_key=None):
        """Sets an AML/KYT customer reference ID for the vault account

        Args:
            vault_account_id (str): The vault account Id
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/set_customer_ref_id",
                                  {"customerRefId": customer_ref_id or ''}, idempotency_key)

    def set_vault_account_customer_ref_id_for_address(self, vault_account_id, asset_id, address, customer_ref_id=None,
                                                      idempotency_key=None):
        """Sets an AML/KYT customer reference ID for the given address

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            address (string): The address for which to set the customer reference id
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}/set_customer_ref_id",
            {"customerRefId": customer_ref_id or ''}, idempotency_key)

    def create_external_wallet(self, name, customer_ref_id=None, idempotency_key=None):
        """Creates a new external wallet

        Args:
            name (str): A name for the new external wallet
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request("/v1/external_wallets", {"name": name, "customerRefId": customer_ref_id or ''},
                                  idempotency_key)

    def create_internal_wallet(self, name, customer_ref_id=None, idempotency_key=None):
        """Creates a new internal wallet

        Args:
            name (str): A name for the new internal wallet
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request("/v1/internal_wallets", {"name": name, "customerRefId": customer_ref_id or ''},
                                  idempotency_key)

    def create_external_wallet_asset(self, wallet_id, asset_id, address, tag=None, idempotency_key=None):
        """Creates a new asset within an exiting external wallet

        Args:
            wallet_id (str): The wallet id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            address (str): The wallet address
            tag (str, optional): (for ripple only) The ripple account tag
            idempotency_key (str, optional)
        """

        body = {"address": address}
        if tag:
            body["tag"] = tag

        return self._post_request(
            f"/v1/external_wallets/{wallet_id}/{asset_id}", body, idempotency_key
        )

    def create_internal_wallet_asset(self, wallet_id, asset_id, address, tag=None, idempotency_key=None):
        """Creates a new asset within an exiting internal wallet

        Args:
            wallet_id (str): The wallet id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            address (str): The wallet address
            tag (str, optional): (for ripple only) The ripple account tag
            idempotency_key (str, optional)
        """

        body = {"address": address}
        if tag:
            body["tag"] = tag

        return self._post_request(
            f"/v1/internal_wallets/{wallet_id}/{asset_id}", body, idempotency_key
        )

    def create_transaction(self, asset_id=None, amount=None, source=None, destination=None, fee=None, gas_price=None,
                           wait_for_status=False, tx_type=TRANSACTION_TRANSFER, note=None, network_fee=None,
                           customer_ref_id=None, replace_tx_by_hash=None, extra_parameters=None, destinations=None,
                           fee_level=None, fail_on_low_fee=None, max_fee=None, gas_limit=None, idempotency_key=None,
                           external_tx_id=None, treat_as_gross_amount=None, force_sweep=None):
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

        return self._post_request("/v1/transactions", body, idempotency_key)

    def delete_internal_wallet(self, wallet_id):
        """Deletes a single internal wallet

        Args:
            wallet_id (string): The internal wallet ID
        """

        return self._delete_request(f"/v1/internal_wallets/{wallet_id}")

    def delete_external_wallet(self, wallet_id):
        """Deletes a single external wallet

        Args:
            wallet_id (string): The external wallet ID
        """

        return self._delete_request(f"/v1/external_wallets/{wallet_id}")

    def delete_internal_wallet_asset(self, wallet_id, asset_id):
        """Deletes a single asset from an internal wallet

        Args:
            wallet_id (string): The internal wallet ID
            asset_id (string): The asset ID
        """

        return self._delete_request(f"/v1/internal_wallets/{wallet_id}/{asset_id}")

    def delete_external_wallet_asset(self, wallet_id, asset_id):
        """Deletes a single asset from an external wallet

        Args:
            wallet_id (string): The external wallet ID
            asset_id (string): The asset ID
        """

        return self._delete_request(f"/v1/external_wallets/{wallet_id}/{asset_id}")

    def set_customer_ref_id_for_internal_wallet(self, wallet_id, customer_ref_id=None, idempotency_key=None):
        """Sets an AML/KYT customer reference ID for the specific internal wallet

        Args:
            wallet_id (string): The external wallet ID
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(f"/v1/internal_wallets/{wallet_id}/set_customer_ref_id",
                                  {"customerRefId": customer_ref_id or ''}, idempotency_key)

    def set_customer_ref_id_for_external_wallet(self, wallet_id, customer_ref_id=None, idempotency_key=None):
        """Sets an AML/KYT customer reference ID for the specific external wallet

        Args:
            wallet_id (string): The external wallet ID
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(f"/v1/external_wallets/{wallet_id}/set_customer_ref_id",
                                  {"customerRefId": customer_ref_id or ''}, idempotency_key)

    def get_transfer_tickets(self):
        """Gets all transfer tickets of your tenant"""

        return self._get_request("/v1/transfer_tickets")

    def create_transfer_ticket(self, terms, external_ticket_id=None, description=None, idempotency_key=None):
        """Creates a new transfer ticket

        Args:
            terms (list of TransferTicketTerm objects): The list of TransferTicketTerm
            external_ticket_id (str, optional): The ID for of the transfer ticket on customer's platform
            description (str, optional): A description for the new ticket
            idempotency_key (str, optional)
        """

        body = {}

        if external_ticket_id:
            body["externalTicketId"] = external_ticket_id

        if description:
            body["description"] = description

        if any([not isinstance(x, TransferTicketTerm) for x in terms]):
            raise FireblocksApiException("Expected Tranfer Assist ticket's term of type TranferTicketTerm")

        body['terms'] = [term.__dict__ for term in terms]

        return self._post_request(f"/v1/transfer_tickets", body, idempotency_key)

    def get_transfer_ticket_by_id(self, ticket_id):
        """Retrieve a transfer ticket

        Args:
            ticket_id (str): The ID of the transfer ticket.
        """

        return self._get_request(f"/v1/transfer_tickets/{ticket_id}")

    def get_transfer_ticket_term(self, ticket_id, term_id):
        """Retrieve a transfer ticket

        Args:
            ticket_id (str): The ID of the transfer ticket
            term_id (str): The ID of the term within the transfer ticket
        """

        return self._get_request(f"/v1/transfer_tickets/{ticket_id}/{term_id}")

    def cancel_transfer_ticket(self, ticket_id, idempotency_key=None):
        """Cancel a transfer ticket

        Args:
            ticket_id (str): The ID of the transfer ticket to cancel
            idempotency_key (str, optional)
        """

        return self._post_request(f"/v1/transfer_tickets/{ticket_id}/cancel", idempotency_key=idempotency_key)

    def execute_ticket_term(self, ticket_id, term_id, source=None, idempotency_key=None):
        """Initiate a transfer ticket transaction

        Args:
            ticket_id (str): The ID of the transfer ticket
            term_id (str): The ID of the term within the transfer ticket
            source (TransferPeerPath): JSON object of the source of the transaction. The network connection's vault account by default
        """

        body = {}

        if source:
            if not isinstance(source, TransferPeerPath):
                raise FireblocksApiException(
                    "Expected ticket term source Of type TransferPeerPath, but got type: " + type(source))
            body["source"] = source.__dict__

        return self._post_request(f"/v1/transfer_tickets/{ticket_id}/{term_id}/transfer", body, idempotency_key)

    def set_confirmation_threshold_for_txid(self, txid, required_confirmations_number, idempotency_key=None):
        """Set the required number of confirmations for transaction

        Args:
            txid (str): The transaction id
            required_confirmations_Number (number): Required confirmation threshold fot the txid
            idempotency_key (str, optional)
        """

        body = {
            "numOfConfirmations": required_confirmations_number
        }

        return self._post_request(f"/v1/transactions/{txid}/set_confirmation_threshold", body, idempotency_key)

    def set_confirmation_threshold_for_txhash(self, txhash, required_confirmations_number, idempotency_key=None):
        """Set the required number of confirmations for transaction by txhash

        Args:
            txhash (str): The transaction hash
            required_confirmations_Number (number): Required confirmation threshold fot the txhash
            idempotency_key (str, optional)
        """

        body = {
            "numOfConfirmations": required_confirmations_number
        }

        return self._post_request(f"/v1/txHash/{txhash}/set_confirmation_threshold", body, idempotency_key)

    def get_public_key_info(self, algorithm, derivation_path, compressed=None):
        """Get the public key information

        Args:
            algorithm (str, optional)
            derivation_path (str)
            compressed (boolean, optional)
        """

        url = "/v1/vault/public_key_info"
        if algorithm:
            url += f"?algorithm={algorithm}"
        if derivation_path:
            url += f"&derivationPath={urllib.parse.quote(derivation_path)}"
        if compressed:
            url += f"&compressed={compressed}"
        return self._get_request(url)

    def get_public_key_info_for_vault_account(self, asset_id, vault_account_id, change, address_index, compressed=None):
        """Get the public key information for a vault account

        Args:
            assetId (str)
            vaultAccountId (number)
            change (number)
            addressIndex (number)
            compressed (boolean, optional)
        """

        url = f"/v1/vault/accounts/{vault_account_id}/{asset_id}/{change}/{address_index}/public_key_info"
        if compressed:
            url += f"?compressed={compressed}"

        return self._get_request(url)

    def allocate_funds_to_private_ledger(self, vault_account_id, asset, allocation_id, amount,
                                         treat_as_gross_amount=None, idempotency_key=None):
        """Allocate funds from your default balance to a private ledger

        Args:
            vault_account_id (string)
            asset (string)
            allocation_id (string)
            amount (string)
            treat_as_gross_amount (bool, optional)
            idempotency_key (string, optional)
        """

        url = f"/v1/vault/accounts/{vault_account_id}/{asset}/lock_allocation"

        return self._post_request(url, {"allocationId": allocation_id, "amount": amount,
                                        "treatAsGrossAmount": treat_as_gross_amount or False}, idempotency_key)

    def deallocate_funds_from_private_ledger(self, vault_account_id, asset, allocation_id, amount,
                                             idempotency_key=None):
        """deallocate funds from a private ledger to your default balance

        Args:
            vault_account_id (string)
            asset (string)
            allocation_id (string)
            amount (string)
            idempotency_key (string, optional)
        """

        url = f"/v1/vault/accounts/{vault_account_id}/{asset}/release_allocation"

        return self._post_request(url, {"allocationId": allocation_id, "amount": amount}, idempotency_key)

    def get_gas_station_info(self, asset_id=None):
        """Get configuration and status of the Gas Station account"
        
        Args:
            asset_id (string, optional)
        """

        url = f"/v1/gas_station"

        if asset_id:
            url = url + f"/{asset_id}"

        return self._get_request(url)

    def set_gas_station_configuration(self, gas_threshold, gas_cap, max_gas_price=None, asset_id=None):
        """Set configuration of the Gas Station account

        Args:
            gasThreshold (str)
            gasCap (str)
            maxGasPrice (str, optional)
            asset_id (str, optional)
        """

        url = f"/v1/gas_station/configuration"
        
        if asset_id:
            url = url + f"/{asset_id}"

        body = {
            "gasThreshold": gas_threshold,
            "gasCap": gas_cap,
            "maxGasPrice": max_gas_price
        }

        return self._put_request(url, body)

    def get_vault_assets_balance(self, account_name_prefix=None, account_name_suffix=None):
        """Gets vault assets accumulated balance

         Args:
            account_name_prefix (string, optional): Vault account name prefix
            account_name_suffix (string, optional): Vault account name suffix
        """
        url = f"/v1/vault/assets"

        params = {}

        if account_name_prefix:
            params['accountNamePrefix'] = account_name_prefix

        if account_name_suffix:
            params['accountNameSuffix'] = account_name_suffix

        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        return self._get_request(url)

    def get_vault_balance_by_asset(self, asset_id=None):
        """Gets vault accumulated balance by asset

         Args:
            asset_id (str, optional): The asset symbol (e.g BTC, ETH)
        """
        url = f"/v1/vault/assets"

        if asset_id:
            url += f"/{asset_id}"

        return self._get_request(url)

    def create_raw_transaction(self, raw_message, source=None, asset_id=None, note=None):
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

    def get_max_spendable_amount(self, vault_account_id, asset_id, manual_signing=False):
        """Get max spendable amount per asset and vault.

        Args:
            vault_account_id (str): The vault account Id.
            asset_id (str): Asset id.
            manual_signing (boolean, optional): False by default.
        """
        url = f"/v1/vault/accounts/{vault_account_id}/{asset_id}/max_spendable_amount?manual_signing={manual_signing}"

        return self._get_request(url)

    def set_auto_fuel(self, vault_account_id, auto_fuel, idempotency_key=None):
        """Sets autoFuel to true/false for a vault account

        Args:
            vault_account_id (str): The vault account Id
            auto_fuel (boolean): The new value for the autoFuel flag
            idempotency_key (str, optional)
        """
        body = {
            "autoFuel": auto_fuel
        }

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/set_auto_fuel", body, idempotency_key)

    def validate_address(self, asset_id, address):
        """Gets vault accumulated balance by asset

         Args:
            asset_id (str): The asset symbol (e.g XRP, EOS)
            address (str): The address to be verified
        """
        url = f"/v1/transactions/validate_address/{asset_id}/{address}"

        return self._get_request(url)

    def resend_webhooks(self):
        """Resend failed webhooks of your tenant"""

        return self._post_request("/v1/webhooks/resend")

    def resend_transaction_webhooks_by_id(self, tx_id, resend_created, resend_status_updated):
        """Resend webhooks of transaction

        Args:
            tx_id (str): The transaction for which the message is sent.
            resend_created (boolean): If true, a webhook will be sent for the creation of the transaction.
            resend_status_updated (boolean): If true, a webhook will be sent for the status of the transaction.
        """
        body = {
            "resendCreated": resend_created,
            "resendStatusUpdated": resend_status_updated
        }

        return self._post_request(f"/v1/webhooks/resend/{tx_id}", body)

    def get_users(self):
        """Gets all users of your tenant"""

        url = "/v1/users"

        return self._get_request(url)

    def get_off_exchanges(self):
        """
        Get your connected off exchanges virtual accounts
        """
        url = f"/v1/off_exchange_accounts"

        return self._get_request(url)

    def get_off_exchange_by_id(self, off_exchange_id):
        """
        Get your connected off exchange by it's ID
        :param off_exchange_id: ID of the off exchange virtual account
        :return: off exchange entity
        """

        url = f"/v1/off_exchange_accounts/{off_exchange_id}"

        return self._get_request(url)

    def settle_off_exchange_by_id(self, off_exchange_id):
        """
        Create a settle request to your off exchange by it's ID
        :param off_exchange_id: ID of the off exchange virtual account
        """

        url = f"/v1/off_exchanges/{off_exchange_id}/settle"

        return self._post_request(url)

    def _get_request(self, path, page_mode=False):
        token = self.token_provider.sign_jwt(path)
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(self.base_url + path, headers=headers, timeout=self.timeout)
        return handle_response(response, page_mode)

    def _delete_request(self, path):
        token = self.token_provider.sign_jwt(path)
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}"
        }

        response = requests.delete(self.base_url + path, headers=headers, timeout=self.timeout)
        return handle_response(response)

    def _post_request(self, path, body={}, idempotency_key=None):
        token = self.token_provider.sign_jwt(path, body)
        if idempotency_key is None:
            headers = {
                "X-API-Key": self.api_key,
                "Authorization": f"Bearer {token}"
            }
        else:
            headers = {
                "X-API-Key": self.api_key,
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": idempotency_key
            }

        response = requests.post(self.base_url + path, headers=headers, json=body, timeout=self.timeout)
        return handle_response(response)

    def _put_request(self, path, body={}):
        token = self.token_provider.sign_jwt(path, body)
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.put(self.base_url + path, headers=headers, data=json.dumps(body), timeout=self.timeout)
        return handle_response(response)
