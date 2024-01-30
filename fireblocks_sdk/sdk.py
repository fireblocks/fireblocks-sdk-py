import json
import platform
import urllib
from importlib.metadata import version
from operator import attrgetter
from typing import Any, Dict, Optional, List, Union

import requests

from .api_types import (
    FireblocksApiException,
    TRANSACTION_TYPES,
    TRANSACTION_STATUS_TYPES,
    TransferPeerPath,
    DestinationTransferPeerPath,
    TransferTicketTerm,
    TRANSACTION_TRANSFER,
    SIGNING_ALGORITHM,
    UnsignedMessage,
    FEE_LEVEL,
    PagedVaultAccountsRequestFilters,
    TransactionDestination,
    GetAssetWalletsFilters,
    TimePeriod,
    GetOwnedCollectionsSortValue,
    OrderValues,
    GetOwnedAssetsSortValues,
    PolicyRule,
    GetSmartTransferFilters,
    NFTOwnershipStatusValues,
    GetOwnedNftsSortValues,
    GetNftsSortValues,
    NFTsWalletTypeValues,
    NFTOwnershipStatusUpdatedPayload,
    PagedExchangeAccountRequestFilters,
    StakeRequestDto,
    UnstakeRequestDto,
    WithdrawRequestDto,
    Role,
    SpamTokenOwnershipValues,
    TokenOwnershipSpamUpdatePayload,
)
from .tokenization_api_types import \
    CreateTokenRequest, \
    ContractUploadRequest, \
    ContractDeployRequest, \
    ReadCallFunction, \
    WriteCallFunction
from .sdk_token_provider import SdkTokenProvider


def handle_response(response, page_mode=False):
    try:
        response_data = response.json()
    except:
        response_data = None
    if response.status_code >= 300:
        if type(response_data) is dict:
            error_code = response_data.get("code")
            raise FireblocksApiException(
                "Got an error from fireblocks server: " + response.text, error_code
            )
        else:
            raise FireblocksApiException(
                "Got an error from fireblocks server: " + response.text
            )
    else:
        if page_mode:
            return {
                "transactions": response_data,
                "pageDetails": {
                    "prevPage": response.headers.get("prev-page", ""),
                    "nextPage": response.headers.get("next-page", ""),
                },
            }
        return response_data


class FireblocksSDK:
    def __init__(
            self,
            private_key,
            api_key,
            api_base_url="https://api.fireblocks.io",
            timeout=None,
            anonymous_platform=False,
            seconds_jwt_exp=55,
    ):
        """Creates a new Fireblocks API Client.

        Args:
            private_key (str): A string representation of your private key (in PEM format)
            api_key (str): Your api key. This is a uuid you received from Fireblocks
            api_base_url (str): The fireblocks server URL. Leave empty to use the default server
            timeout (number): Timeout for http requests in seconds
        """
        self.private_key = private_key
        self.api_key = api_key
        self.base_url = api_base_url
        self.token_provider = SdkTokenProvider(private_key, api_key, seconds_jwt_exp)
        self.timeout = timeout
        self.http_session = requests.Session()
        self.http_session.headers.update(
            {
                "X-API-Key": self.api_key,
                "User-Agent": self._get_user_agent(anonymous_platform),
            }
        )

    def get_staking_chains(self):
        """Get all staking chains."""
        return self._get_request("/v1/staking/chains")

    def get_staking_chain_info(self, chain_descriptor: str):
        """Get chain info."""
        return self._get_request(f"/v1/staking/chains/{chain_descriptor}/chainInfo")

    def get_staking_positions_summary(self):
        """Get staking positions summary."""
        return self._get_request(f"/v1/staking/positions/summary")

    def get_staking_positions_summary_by_vault(self):
        """Get staking positions summary by vault."""
        return self._get_request("/v1/staking/positions/summary/vaults")

    def execute_staking_action(self, chain_descriptor: str, action_id: str,
                               request_body: Union[StakeRequestDto, UnstakeRequestDto, WithdrawRequestDto]):
        """Execute staking action on a chain.
        """
        return self._post_request(f"/v1/staking/chains/{chain_descriptor}/{action_id}", request_body.to_dict())

    def get_staking_positions(self, chain_descriptor: str = None):
        """Get all staking positions, optionally filtered by chain."""
        return self._get_request("/v1/staking/positions",
                                 query_params={"chainDescriptor": chain_descriptor} if chain_descriptor else None)

    def get_staking_position(self, position_id: str):
        """Get a staking position by id."""
        return self._get_request(f"/v1/staking/positions/{position_id}")

    def get_staking_providers(self):
        """Get all staking providers."""
        return self._get_request(f"/v1/staking/providers")

    def approve_staking_provider_terms_of_service(self, provider_id: str):
        """Approve staking provider terms of service."""
        return self._post_request(f"/v1/staking/providers/{provider_id}/approveTermsOfService")

    def get_nft(self, id: str):
        url = "/v1/nfts/tokens/" + id

        return self._get_request(url)

    def get_nfts(
            self,
            ids: List[str],
            page_cursor: str = "",
            page_size: int = 100,
            sort: List[GetNftsSortValues] = None,
            order: OrderValues = None,
    ):
        """
        Example list: "[1,2,3,4]"

        """
        url = f"/v1/nfts/tokens"

        if len(ids) <= 0:
            raise FireblocksApiException(
                "Invalid token_ids. Should contain at least 1 token id"
            )

        params = {
            "ids": ",".join(ids),
        }

        if page_cursor:
            params["pageCursor"] = page_cursor

        if page_size:
            params["pageSize"] = page_size

        if sort:
            params["sort"] = ",".join(sort)

        if order:
            params["order"] = order.value

        return self._get_request(url, query_params=params)

    def refresh_nft_metadata(self, id: str):
        """

        :param id:
        :return:
        """
        url = "/v1/nfts/tokens/" + id
        return self._put_request(path=url)

    def refresh_nft_ownership_by_vault(
            self, blockchain_descriptor: str, vault_account_id: str
    ):
        """

        :param blockchain_descriptor:
        :param vault_account_id:
        :return:
        """
        url = "/v1/nfts/ownership/tokens"

        params = {}
        if blockchain_descriptor:
            params["blockchainDescriptor"] = blockchain_descriptor

        if vault_account_id:
            params["vaultAccountId"] = vault_account_id

        return self._put_request(url, query_params=params)

    def get_owned_nfts(self, blockchain_descriptor: str, vault_account_ids: List[str] = None, ids: List[str] = None,
                       collection_ids: List[str] = None, page_cursor: str = '', page_size: int = 100,
                       sort: List[GetOwnedNftsSortValues] = None,
                       order: OrderValues = None, status: NFTOwnershipStatusValues = None, search: str = None,
                       ncw_account_ids: List[str] = None, ncw_id: str = None, wallet_type: NFTsWalletTypeValues = None, spam: SpamTokenOwnershipValues = None):
        """

        """
        url = f"/v1/nfts/ownership/tokens"

        params = {}

        if blockchain_descriptor:
            params["blockchainDescriptor"] = blockchain_descriptor

        if vault_account_ids:
            params["vaultAccountIds"] = ",".join(vault_account_ids)

        if ids:
            params["ids"] = ",".join(ids)

        if collection_ids:
            params["collectionIds"] = ",".join(collection_ids)

        if ncw_account_ids:
            params['ncwAccountIds'] = ",".join(ncw_account_ids)

        if ncw_id:
            params['ncwId'] = ncw_id.value

        if wallet_type:
            params['walletType'] = wallet_type.value

        if page_cursor:
            params["pageCursor"] = page_cursor

        if page_size:
            params["pageSize"] = page_size

        if sort:
            params["sort"] = ",".join(sort)

        if order:
            params["order"] = order.value

        if status:
            params["status"] = status.value

        if search:
            params["search"] = search

        if spam:
            params["spam"] = spam.value

        return self._get_request(url, query_params=params)

    def list_owned_collections(self, search: str = None, status: NFTOwnershipStatusValues = None,
                               ncw_id: str = None, wallet_type: NFTsWalletTypeValues = None,
                               sort: List[GetOwnedCollectionsSortValue] = None,
                               order: OrderValues = None, page_cursor: str = '', page_size: int = 100):
        """

        """
        url = f"/v1/nfts/ownership/collections"

        params = {}

        if search:
            params['search'] = search

        if status:
            params['status'] = status.value

        if ncw_id:
            params['ncwId'] = ncw_id.value

        if wallet_type:
            params['walletType'] = wallet_type.value

        if page_cursor:
            params['pageCursor'] = page_cursor

        if page_size:
            params['pageSize'] = page_size

        if sort:
            params['sort'] = ",".join(sort)

        if order:
            params['order'] = order.value

        return self._get_request(url, query_params=params)

    def list_owned_assets(self, search: str = None, status: NFTOwnershipStatusValues = None,
                          ncw_id: str = None, wallet_type: NFTsWalletTypeValues = None,
                          sort: List[GetOwnedAssetsSortValues] = None,
                          order: OrderValues = None, page_cursor: str = '', page_size: int = 100, spam: SpamTokenOwnershipValues = None):
        """
        """
        url = f"/v1/nfts/ownership/assets"

        params = {}

        if search:
            params['search'] = search

        if status:
            params['status'] = status.value

        if ncw_id:
            params['ncwId'] = ncw_id.value

        if wallet_type:
            params['walletType'] = wallet_type.value

        if page_cursor:
            params["pageCursor"] = page_cursor

        if page_size:
            params["pageSize"] = page_size

        if sort:
            params["sort"] = ",".join(sort)

        if order:
            params['order'] = order

        if spam:
            params["spam"] = spam.value

        return self._get_request(url, query_params=params)

    def update_nft_ownership_status(self, id: str, status: NFTOwnershipStatusValues):
        """Update NFT ownership status for specific token

        Args:
            id (string): NFT asset id
            status (string): Status for update
        """
        url = "/v1/nfts/ownership/tokens/" + id + "/status"

        return self._put_request(url, {"status": status.value})

    def update_nft_ownerships_status(self, payload: List[NFTOwnershipStatusUpdatedPayload]):
        """Updates tokens status for a tenant, in all tenant vaults.

        Args:
            payload (NFTOwnershipStatusUpdatedPayload[]): List of assets with status for update
        """
        url = "/v1/nfts/ownership/tokens/status"

        return self._put_request(url, list(map((lambda payload_item: payload_item.serialize()), payload)))

        def update_nft_token_ownerships_spam_status(self, payload: List[TokenOwnershipSpamUpdatePayload]):
            """Updates tokens spam status for a tenant, in all tenant vaults.

            Args:
                payload (TokenOwnershipSpamUpdatePayload[]): List of assets with status for update
            """
            url = "/v1/nfts/ownership/tokens/spam"

            return self._put_request(url, list(map((lambda payload_item: payload_item.serialize()), payload)))

    def get_supported_assets(self):
        """Gets all assets that are currently supported by Fireblocks"""

        return self._get_request("/v1/supported_assets")

    def get_vault_accounts_with_page_info(
            self, paged_vault_accounts_request_filters: PagedVaultAccountsRequestFilters
    ):
        """Gets a page of vault accounts for your tenant according to filters given

        Args:
            paged_vault_accounts_request_filters (object, optional): Possible filters to apply for request
        """

        url = f"/v1/vault/accounts_paged"
        (
            name_prefix,
            name_suffix,
            min_amount_threshold,
            asset_id,
            order_by,
            limit,
            before,
            after,
        ) = attrgetter(
            "name_prefix",
            "name_suffix",
            "min_amount_threshold",
            "asset_id",
            "order_by",
            "limit",
            "before",
            "after",
        )(
            paged_vault_accounts_request_filters
        )

        params = {}

        if name_prefix:
            params["namePrefix"] = name_prefix

        if name_suffix:
            params["nameSuffix"] = name_suffix

        if min_amount_threshold is not None:
            params["minAmountThreshold"] = min_amount_threshold

        if asset_id is not None:
            params["assetId"] = asset_id

        if order_by is not None:
            params["orderBy"] = order_by

        if limit is not None:
            params["limit"] = limit

        if before is not None:
            params["before"] = before

        if after is not None:
            params["after"] = after

        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        return self._get_request(url)

    def get_asset_wallets(self, get_vault_wallets_filters: GetAssetWalletsFilters):
        """Optional filters to apply for request

        Args
            total_amount_larger_than (number, optional):  The minimum amount for asset to have in order to be included in the results
            asset_id (string, optional): The asset symbol
            order_by (ASC/DESC, optional): Order of results by vault creation time (default: DESC)
            limit (number, optional): Results page size
            before (string, optional): cursor string received from previous request
            after (string, optional): cursor string received from previous request

        Constraints
            - You should only insert 'before' or 'after' (or none of them), but not both
        """
        url = f"/v1/vault/asset_wallets"

        total_amount_larger_than, asset_id, order_by, limit, before, after = attrgetter(
            "total_amount_larger_than",
            "asset_id",
            "order_by",
            "limit",
            "before",
            "after",
        )(get_vault_wallets_filters)

        params = {}

        if total_amount_larger_than is not None:
            params["totalAmountLargerThan"] = total_amount_larger_than

        if asset_id is not None:
            params["assetId"] = asset_id

        if order_by is not None:
            params["orderBy"] = order_by

        if limit is not None:
            params["limit"] = limit

        if before is not None:
            params["before"] = before

        if after is not None:
            params["after"] = after

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

    def refresh_vault_asset_balance(
            self, vault_account_id, asset_id, idempotency_key=None
    ):
        """Gets a single vault account asset after forcing refresh from the blockchain
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/balance",
            {},
            idempotency_key,
        )

    def get_deposit_addresses(self, vault_account_id, asset_id):
        """Gets deposit addresses for an asset in a vault account
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self._get_request(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses"
        )

    def get_unspent_inputs(self, vault_account_id, asset_id):
        """Gets utxo list for an asset in a vault account
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (like BTC, DASH and utxo based assets)
        """

        return self._get_request(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/unspent_inputs"
        )

    def generate_new_address(
            self,
            vault_account_id,
            asset_id,
            description=None,
            customer_ref_id=None,
            idempotency_key=None,
    ):
        """Generates a new address for an asset in a vault account

        Args:
            vault_account_id (string): The vault account ID
            asset_id (string): The ID of the asset for which to generate the deposit address
            description (string, optional): A description for the new address
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses",
            {"description": description or "", "customerRefId": customer_ref_id or ""},
            idempotency_key,
        )

    def set_address_description(
            self, vault_account_id, asset_id, address, tag=None, description=None
    ):
        """Sets the description of an existing address

        Args:
            vault_account_id (string): The vault account ID
            asset_id (string): The ID of the asset
            address (string): The address for which to set the set_address_description
            tag (string, optional): The XRP tag, or EOS memo, for which to set the description
            description (string, optional): The description to set, or none for no description
        """
        if tag:
            return self._put_request(
                f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}:{tag}",
                {"description": description or ""},
            )
        else:
            return self._put_request(
                f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}",
                {"description": description or ""},
            )

    def get_network_connections(self):
        """Gets all network connections for your tenant"""

        return self._get_request("/v1/network_connections")

    def create_network_connection(
            self,
            local_network_id: str,
            remote_network_id: str,
            routing_policy=None,
            idempotency_key=None,
    ):
        """Creates a network connection
        Args:
            localNetworkId (str): The local netowrk profile's id
            remoteNetworkId (str): The remote network profile's id
            routingPolicy (RoutingPolicy): The desired routing policy for the connection
        """

        body = {
            "localNetworkId": local_network_id,
            "remoteNetworkId": remote_network_id,
            "routingPolicy": routing_policy or {},
        }

        return self._post_request(f"/v1/network_connections", body, idempotency_key)

    def get_network_connection_by_id(self, connection_id: str):
        """Gets a single network connection
        Args:
            connection_id (string): The network connection's id
        """

        return self._get_request(f"/v1/network_connections/{connection_id}")

    def remove_network_connection(self, connection_id: str):
        """Removes a network connection
        Args:
            connection_id (string): The network connection's id
        """

        return self._delete_request(f"/v1/network_connections/{connection_id}")

    def set_network_connection_routing_policy(
            self, connection_id: str, routing_policy=None
    ):
        """Sets routing policy for a network connection
        Args:
            connection_id (string): The network connection's id
            routing_policy (routingPolicy): The desired routing policy
        """

        body = {"routingPolicy": routing_policy or {}}

        return self._patch_request(
            f"/v1/network_connections/{connection_id}/set_routing_policy", body
        )

    def get_discoverable_network_ids(self):
        """Gets all discoverable network profiles"""

        return self._get_request(f"/v1/network_ids")

    def create_network_id(self, name: str, routing_policy=None):
        """Creates a new network profile
        Args:
            name (str): A name for the new network profile
            routing_policy (routingPolicy): The desired routing policy for the network
        """

        body = {"name": name, "routingPolicy": routing_policy or {}}

        return self._post_request(f"/v1/network_ids", body)

    def get_network_id(self, network_id: str):
        """Gets a single network profile
        Args:
            network_id (str): The network profile's id
        """

        return self._get_request(f"/v1/network_ids/{network_id}")

    def delete_network_id(self, network_id: str):
        """Deletes a single network profile
        Args:
            network_id (str): The network profile's id
        """

        return self._delete_request(f"/v1/network_ids/{network_id}")

    def set_network_id_discoverability(self, network_id: str, is_discoverable: bool):
        """Sets discoverability for network profile
        Args:
            network_id (str): The network profile's id
            is_discoverable: (bool) The desired discoverability to set
        """

        body = {"isDiscoverable": is_discoverable}

        return self._patch_request(
            f"/v1/network_ids/{network_id}/set_discoverability", body
        )

    def set_network_id_routing_policy(self, network_id: str, routing_policy):
        """Sets routing policy for network profile
        Args:
            network_id (str): The network profile's id
            routing_policy: (routingPolicy) The desired routing policy
        """

        body = {"routingPolicy": routing_policy}

        return self._patch_request(
            f"/v1/network_ids/{network_id}/set_routing_policy", body
        )

    def set_network_id_name(self, network_id: str, name: str):
        """Sets network profile name
        Args:
            network_id (str): The network profile's id
            name: (str) The desired network profile's name
        """

        body = {"name": name}

        return self._patch_request(f"/v1/network_ids/{network_id}/set_name", body)

    def get_exchange_accounts(self):
        """Gets all exchange accounts for your tenant"""

        return self._get_request("/v1/exchange_accounts")

    def get_exchange_accounts_paged(self, paged_exchange_accounts_request_filters: PagedExchangeAccountRequestFilters):
        """Gets a page of vault accounts for your tenant according to filters given

        Args:
            paged_exchange_accounts_request_filters (object, optional): Possible filters to apply for request
        """

        url = f"/v1/exchange_accounts/paged"
        limit, before, after = \
            attrgetter('limit', 'before', 'after')(
                paged_exchange_accounts_request_filters)

        params = {}

        if limit is not None:
            params['limit'] = limit

        if before is not None:
            params['before'] = before

        if after is not None:
            params['after'] = after

        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        return self._get_request(url)

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

        return self._get_request(
            f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}"
        )

    def transfer_to_subaccount(
            self, exchange_account_id, subaccount_id, asset_id, amount, idempotency_key=None
    ):
        """Transfer to a subaccount from a main exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            subaccount_id (string): The ID of the subaccount in the exchange
            asset_id (string): The asset to transfer
            amount (double): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {"subaccountId": subaccount_id, "amount": amount}

        return self._post_request(
            f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}/transfer_to_subaccount",
            body,
            idempotency_key,
        )

    def transfer_from_subaccount(
            self, exchange_account_id, subaccount_id, asset_id, amount, idempotency_key=None
    ):
        """Transfer from a subaccount to a main exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            subaccount_id (string): The ID of the subaccount in the exchange
            asset_id (string): The asset to transfer
            amount (double): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {"subaccountId": subaccount_id, "amount": amount}

        return self._post_request(
            f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}/transfer_from_subaccount",
            body,
            idempotency_key,
        )

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

        return self._post_request(
            f"/v1/fiat_accounts/{account_id}/redeem_to_linked_dda",
            body,
            idempotency_key,
        )

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

        return self._post_request(
            f"/v1/fiat_accounts/{account_id}/deposit_from_linked_dda",
            body,
            idempotency_key,
        )

    def get_transactions_with_page_info(
            self,
            before=0,
            after=None,
            status=None,
            limit=None,
            txhash=None,
            assets=None,
            source_type=None,
            source_id=None,
            dest_type=None,
            dest_id=None,
            next_or_previous_path=None,
    ):
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
                return {
                    "transactions": [],
                    "pageDetails": {"prevPage": "", "nextPage": ""},
                }
            index = next_or_previous_path.index("/v1/")
            length = len(next_or_previous_path) - 1
            suffix_path = next_or_previous_path[index:length]
            return self._get_request(suffix_path, True)
        else:
            return self._get_transactions(
                before,
                after,
                status,
                limit,
                None,
                txhash,
                assets,
                source_type,
                source_id,
                dest_type,
                dest_id,
                True,
            )

    def get_transactions(
            self,
            before=0,
            after=0,
            status=None,
            limit=None,
            order_by=None,
            txhash=None,
            assets=None,
            source_type=None,
            source_id=None,
            dest_type=None,
            dest_id=None,
    ):
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
        return self._get_transactions(
            before,
            after,
            status,
            limit,
            order_by,
            txhash,
            assets,
            source_type,
            source_id,
            dest_type,
            dest_id,
        )

    def _get_transactions(
            self,
            before,
            after,
            status,
            limit,
            order_by,
            txhash,
            assets,
            source_type,
            source_id,
            dest_type,
            dest_id,
            page_mode=False,
    ):
        path = "/v1/transactions"
        params = {}

        if status and status not in TRANSACTION_STATUS_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + status)

        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        if order_by:
            params["orderBy"] = order_by
        if txhash:
            params["txHash"] = txhash
        if assets:
            params["assets"] = assets
        if source_type:
            params["sourceType"] = source_type
        if source_id:
            params["sourceId"] = source_id
        if dest_type:
            params["destType"] = dest_type
        if dest_id:
            params["destId"] = dest_id
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

    def get_contract_wallets(self):
        """Gets all contract wallets for your tenant"""
        return self._get_request(f"/v1/contracts")

    def get_contract_wallet(self, wallet_id):
        """Gets a single contract wallet

        Args:
        wallet_id (str): The contract wallet ID
        """
        return self._get_request(f"/v1/contracts/{wallet_id}")

    def get_contract_wallet_asset(self, wallet_id, asset_id):
        """Gets a single contract wallet asset

        Args:
        wallet_id (str): The contract wallet ID
        asset_id (str): The asset ID
        """
        return self._get_request(f"/v1/contracts/{wallet_id}/{asset_id}")

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

    def estimate_fee_for_transaction(
            self,
            asset_id,
            amount,
            source,
            destination=None,
            tx_type=TRANSACTION_TRANSFER,
            idempotency_key=None,
            destinations=None,
    ):
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
                "Expected transaction source of type TransferPeerPath, but got type: "
                + type(source)
            )

        body = {
            "assetId": asset_id,
            "amount": amount,
            "source": source.__dict__,
            "operation": tx_type,
        }

        if destination:
            if not isinstance(
                    destination, (TransferPeerPath, DestinationTransferPeerPath)
            ):
                raise FireblocksApiException(
                    "Expected transaction fee estimation destination of type DestinationTransferPeerPath or TransferPeerPath, but got type: "
                    + type(destination)
                )
            body["destination"] = destination.__dict__

        if destinations:
            if any([not isinstance(x, TransactionDestination) for x in destinations]):
                raise FireblocksApiException(
                    "Expected destinations of type TransactionDestination"
                )
            body["destinations"] = [dest.__dict__ for dest in destinations]

        return self._post_request(
            "/v1/transactions/estimate_fee", body, idempotency_key
        )

    def cancel_transaction_by_id(self, txid, idempotency_key=None):
        """Cancels the selected transaction

        Args:
            txid (str): The transaction id to cancel
            idempotency_key (str, optional)
        """

        return self._post_request(
            f"/v1/transactions/{txid}/cancel", idempotency_key=idempotency_key
        )

    def drop_transaction(
            self, txid, fee_level=None, requested_fee=None, idempotency_key=None
    ):
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

        return self._post_request(
            f"/v1/transactions/{txid}/drop", body, idempotency_key
        )

    def create_vault_account(
            self,
            name,
            hiddenOnUI=False,
            customer_ref_id=None,
            autoFuel=False,
            idempotency_key=None,
    ):
        """Creates a new vault account.

        Args:
            name (str): A name for the new vault account
            hiddenOnUI (boolean): Specifies whether the vault account is hidden from the web console, false by default
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """
        body = {"name": name, "hiddenOnUI": hiddenOnUI, "autoFuel": autoFuel}

        if customer_ref_id:
            body["customerRefId"] = customer_ref_id

        return self._post_request("/v1/vault/accounts", body, idempotency_key)

    def hide_vault_account(self, vault_account_id, idempotency_key=None):
        """Hides the vault account from being visible in the web console

        Args:
            vault_account_id (str): The vault account Id
            idempotency_key (str, optional)
        """
        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/hide",
            idempotency_key=idempotency_key,
        )

    def unhide_vault_account(self, vault_account_id, idempotency_key=None):
        """Returns the vault account to being visible in the web console

        Args:
            vault_account_id (str): The vault account Id
            idempotency_key (str, optional)
        """
        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/unhide",
            idempotency_key=idempotency_key,
        )

    def freeze_transaction_by_id(self, txId, idempotency_key=None):
        """Freezes the selected transaction

        Args:
            txId (str): The transaction ID to freeze
            idempotency_key (str, optional)
        """
        return self._post_request(
            f"/v1/transactions/{txId}/freeze", idempotency_key=idempotency_key
        )

    def unfreeze_transaction_by_id(self, txId, idempotency_key=None):
        """Unfreezes the selected transaction

        Args:
            txId (str): The transaction ID to unfreeze
            idempotency_key (str, optional)
        """
        return self._post_request(
            f"/v1/transactions/{txId}/unfreeze", idempotency_key=idempotency_key
        )

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

        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}",
            idempotency_key=idempotency_key,
        )

    def activate_vault_asset(self, vault_account_id, asset_id, idempotency_key=None):
        """Retry to create a vault asset for a vault asset that failed

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            idempotency_key (str, optional)
        """

        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/activate",
            idempotency_key=idempotency_key,
        )

    def set_vault_account_customer_ref_id(
            self, vault_account_id, customer_ref_id, idempotency_key=None
    ):
        """Sets an AML/KYT customer reference ID for the vault account

        Args:
            vault_account_id (str): The vault account Id
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/set_customer_ref_id",
            {"customerRefId": customer_ref_id or ""},
            idempotency_key,
        )

    def set_vault_account_customer_ref_id_for_address(
            self,
            vault_account_id,
            asset_id,
            address,
            customer_ref_id=None,
            idempotency_key=None,
    ):
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
            {"customerRefId": customer_ref_id or ""},
            idempotency_key,
        )

    def create_contract_wallet(self, name, idempotency_key=None):
        """Creates a new contract wallet

        Args:
        name (str): A name for the new contract wallet
        """
        return self._post_request("/v1/contracts", {"name": name}, idempotency_key)

    def create_contract_wallet_asset(
            self, wallet_id, assetId, address, tag=None, idempotency_key=None
    ):
        """Creates a new contract wallet asset

        Args:
        wallet_id (str): The wallet id
        assetId (str): The asset to add
        address (str): The wallet address
        tag (str): (for ripple only) The ripple account tag
        """
        return self._post_request(
            f"/v1/contracts/{wallet_id}/{assetId}",
            {"address": address, "tag": tag},
            idempotency_key,
        )

    def create_external_wallet(self, name, customer_ref_id=None, idempotency_key=None):
        """Creates a new external wallet

        Args:
            name (str): A name for the new external wallet
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(
            "/v1/external_wallets",
            {"name": name, "customerRefId": customer_ref_id or ""},
            idempotency_key,
        )

    def create_internal_wallet(self, name, customer_ref_id=None, idempotency_key=None):
        """Creates a new internal wallet

        Args:
            name (str): A name for the new internal wallet
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(
            "/v1/internal_wallets",
            {"name": name, "customerRefId": customer_ref_id or ""},
            idempotency_key,
        )

    def create_external_wallet_asset(
            self, wallet_id, asset_id, address, tag=None, idempotency_key=None
    ):
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

    def create_internal_wallet_asset(
            self, wallet_id, asset_id, address, tag=None, idempotency_key=None
    ):
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

    def create_transaction(
            self,
            asset_id=None,
            amount=None,
            source=None,
            destination=None,
            fee=None,
            gas_price=None,
            wait_for_status=False,
            tx_type=TRANSACTION_TRANSFER,
            note=None,
            network_fee=None,
            customer_ref_id=None,
            replace_tx_by_hash=None,
            extra_parameters=None,
            destinations=None,
            fee_level=None,
            fail_on_low_fee=None,
            max_fee=None,
            gas_limit=None,
            idempotency_key=None,
            external_tx_id=None,
            treat_as_gross_amount=None,
            force_sweep=None,
            priority_fee=None,
    ):
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
            priority_fee (number, optional): The priority fee of Ethereum transaction according to EIP-1559
        """

        if tx_type not in TRANSACTION_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + tx_type)

        if source:
            if not isinstance(source, TransferPeerPath):
                raise FireblocksApiException(
                    "Expected transaction source of type TransferPeerPath, but got type: "
                    + type(source)
                )

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
            if not isinstance(
                    destination, (TransferPeerPath, DestinationTransferPeerPath)
            ):
                raise FireblocksApiException(
                    "Expected transaction destination of type DestinationTransferPeerPath or TransferPeerPath, but got type: "
                    + type(destination)
                )
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
                raise FireblocksApiException(
                    "Expected destinations of type TransactionDestination"
                )

            body["destinations"] = [dest.__dict__ for dest in destinations]

        if extra_parameters:
            body["extraParameters"] = extra_parameters

        if external_tx_id:
            body["externalTxId"] = external_tx_id

        if force_sweep:
            body["forceSweep"] = force_sweep

        if priority_fee:
            body["priorityFee"] = priority_fee

        return self._post_request("/v1/transactions", body, idempotency_key)

    def delete_contract_wallet(self, wallet_id):
        """Deletes a single contract wallet

        Args:
            wallet_id (string): The contract wallet ID
        """
        return self._delete_request(f"/v1/contracts/{wallet_id}")

    def delete_contract_wallet_asset(self, wallet_id, asset_id):
        """Deletes a single contract wallet

        Args:
            wallet_id (string): The contract wallet ID
            asset_id (string): The asset ID
        """

        return self._delete_request(f"/v1/contracts/{wallet_id}/{asset_id}")

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

    def set_customer_ref_id_for_internal_wallet(
            self, wallet_id, customer_ref_id=None, idempotency_key=None
    ):
        """Sets an AML/KYT customer reference ID for the specific internal wallet

        Args:
            wallet_id (string): The external wallet ID
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(
            f"/v1/internal_wallets/{wallet_id}/set_customer_ref_id",
            {"customerRefId": customer_ref_id or ""},
            idempotency_key,
        )

    def set_customer_ref_id_for_external_wallet(
            self, wallet_id, customer_ref_id=None, idempotency_key=None
    ):
        """Sets an AML/KYT customer reference ID for the specific external wallet

        Args:
            wallet_id (string): The external wallet ID
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self._post_request(
            f"/v1/external_wallets/{wallet_id}/set_customer_ref_id",
            {"customerRefId": customer_ref_id or ""},
            idempotency_key,
        )

    def get_transfer_tickets(self):
        """Gets all transfer tickets of your tenant"""

        return self._get_request("/v1/transfer_tickets")

    def create_transfer_ticket(
            self, terms, external_ticket_id=None, description=None, idempotency_key=None
    ):
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
            raise FireblocksApiException(
                "Expected Tranfer Assist ticket's term of type TranferTicketTerm"
            )

        body["terms"] = [term.__dict__ for term in terms]

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

        return self._post_request(
            f"/v1/transfer_tickets/{ticket_id}/cancel", idempotency_key=idempotency_key
        )

    def execute_ticket_term(
            self, ticket_id, term_id, source=None, idempotency_key=None
    ):
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
                    "Expected ticket term source Of type TransferPeerPath, but got type: "
                    + type(source)
                )
            body["source"] = source.__dict__

        return self._post_request(
            f"/v1/transfer_tickets/{ticket_id}/{term_id}/transfer",
            body,
            idempotency_key,
        )

    def set_confirmation_threshold_for_txid(
            self, txid, required_confirmations_number, idempotency_key=None
    ):
        """Set the required number of confirmations for transaction

        Args:
            txid (str): The transaction id
            required_confirmations_Number (number): Required confirmation threshold fot the txid
            idempotency_key (str, optional)
        """

        body = {"numOfConfirmations": required_confirmations_number}

        return self._post_request(
            f"/v1/transactions/{txid}/set_confirmation_threshold", body, idempotency_key
        )

    def set_confirmation_threshold_for_txhash(
            self, txhash, required_confirmations_number, idempotency_key=None
    ):
        """Set the required number of confirmations for transaction by txhash

        Args:
            txhash (str): The transaction hash
            required_confirmations_Number (number): Required confirmation threshold fot the txhash
            idempotency_key (str, optional)
        """

        body = {"numOfConfirmations": required_confirmations_number}

        return self._post_request(
            f"/v1/txHash/{txhash}/set_confirmation_threshold", body, idempotency_key
        )

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

    def get_public_key_info_for_vault_account(
            self, asset_id, vault_account_id, change, address_index, compressed=None
    ):
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

    def allocate_funds_to_private_ledger(
            self,
            vault_account_id,
            asset,
            allocation_id,
            amount,
            treat_as_gross_amount=None,
            idempotency_key=None,
    ):
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

        return self._post_request(
            url,
            {
                "allocationId": allocation_id,
                "amount": amount,
                "treatAsGrossAmount": treat_as_gross_amount or False,
            },
            idempotency_key,
        )

    def deallocate_funds_from_private_ledger(
            self, vault_account_id, asset, allocation_id, amount, idempotency_key=None
    ):
        """deallocate funds from a private ledger to your default balance

        Args:
            vault_account_id (string)
            asset (string)
            allocation_id (string)
            amount (string)
            idempotency_key (string, optional)
        """

        url = f"/v1/vault/accounts/{vault_account_id}/{asset}/release_allocation"

        return self._post_request(
            url, {"allocationId": allocation_id, "amount": amount}, idempotency_key
        )

    def get_gas_station_info(self, asset_id=None):
        """Get configuration and status of the Gas Station account"

        Args:
            asset_id (string, optional)
        """

        url = f"/v1/gas_station"

        if asset_id:
            url = url + f"/{asset_id}"

        return self._get_request(url)

    def set_gas_station_configuration(
            self, gas_threshold, gas_cap, max_gas_price=None, asset_id=None
    ):
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
            "maxGasPrice": max_gas_price,
        }

        return self._put_request(url, body)

    def get_vault_assets_balance(
            self, account_name_prefix=None, account_name_suffix=None
    ):
        """Gets vault assets accumulated balance

        Args:
           account_name_prefix (string, optional): Vault account name prefix
           account_name_suffix (string, optional): Vault account name suffix
        """
        url = f"/v1/vault/assets"

        params = {}

        if account_name_prefix:
            params["accountNamePrefix"] = account_name_prefix

        if account_name_suffix:
            params["accountNameSuffix"] = account_name_suffix

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

    def create_raw_transaction(
            self, raw_message, source=None, asset_id=None, note=None
    ):
        """Creates a new raw transaction with the specified parameters

        Args:
            raw_message (RawMessage): The messages that should be signed
            source (TransferPeerPath, optional): The transaction source
            asset_id (str, optional): Transaction asset id
            note (str, optional): A custome note that can be associated with the transaction
        """

        if asset_id is None:
            if raw_message.algorithm not in SIGNING_ALGORITHM:
                raise Exception(
                    "Got invalid signing algorithm type: " + raw_message.algorithm
                )

        if not all([isinstance(x, UnsignedMessage) for x in raw_message.messages]):
            raise FireblocksApiException("Expected messages of type UnsignedMessage")

        raw_message.messages = [message.__dict__ for message in raw_message.messages]

        return self.create_transaction(
            asset_id,
            source=source,
            tx_type="RAW",
            extra_parameters={"rawMessageData": raw_message.__dict__},
            note=note,
        )

    def get_max_spendable_amount(
            self, vault_account_id, asset_id, manual_signing=False
    ):
        """Get max spendable amount per asset and vault.

        Args:
            vault_account_id (str): The vault account Id.
            asset_id (str): Asset id.
            manual_signing (boolean, optional): False by default.
        """
        url = f"/v1/vault/accounts/{vault_account_id}/{asset_id}/max_spendable_amount?manual_signing={manual_signing}"

        return self._get_request(url)

    def get_max_bip44_index_used(self, vault_account_id, asset_id):
        """Get maximum BIP44 index used in deriving addresses or in change addresses.

        Args:
            vault_account_id (str): The vault account Id.
            asset_id (str): Asset id.
        """
        url = f"/v1/vault/accounts/{vault_account_id}/{asset_id}/max_bip44_index_used"

        return self._get_request(url)

    def get_paginated_addresses(self, vault_account_id, asset_id, limit=500, before=None, after=None):
        """Gets a paginated response of the addresses for a given vault account and asset
        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): the asset Id
            limit(number, optional): limit of addresses per paging request
            before (str, optional): curser for the previous paging
            after (str, optional): curser for the next paging
        """
        path = f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses_paginated"
        params = {}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if params:
            path = path + "?" + urllib.parse.urlencode(params)
        return self._get_request(path)

    def set_auto_fuel(self, vault_account_id, auto_fuel, idempotency_key=None):
        """Sets autoFuel to true/false for a vault account

        Args:
            vault_account_id (str): The vault account Id
            auto_fuel (boolean): The new value for the autoFuel flag
            idempotency_key (str, optional)
        """
        body = {"autoFuel": auto_fuel}

        return self._post_request(
            f"/v1/vault/accounts/{vault_account_id}/set_auto_fuel",
            body,
            idempotency_key,
        )

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

    def resend_transaction_webhooks_by_id(
            self, tx_id, resend_created, resend_status_updated
    ):
        """Resend webhooks of transaction

        Args:
            tx_id (str): The transaction for which the message is sent.
            resend_created (boolean): If true, a webhook will be sent for the creation of the transaction.
            resend_status_updated (boolean): If true, a webhook will be sent for the status of the transaction.
        """
        body = {
            "resendCreated": resend_created,
            "resendStatusUpdated": resend_status_updated,
        }

        return self._post_request(f"/v1/webhooks/resend/{tx_id}", body)

    def get_users(self) -> List[Dict[str, Any]]:
        """
        Gets all Users for your tenant
        """

        url = "/v1/users"

        return self._get_request(url)

    def get_ota_configuration(self) -> Dict[str, Any]:
        """
        Get the tenant's OTA (One-Time-Address) configuration
        """

        url = "/v1/management/ota"

        return self._get_request(url)

    def update_ota_configuration(self, enable: bool) -> None:
        """
        Update the tenant's OTA (One-Time-Address) configuration
        @param enable
        """

        url = "/v1/management/ota"

        body = {
            "enabled": enable
        }

        return self._put_request(url, body)

    def get_user_groups(self) -> List[Dict[str, Any]]:
        """
        Gets all User Groups for your tenant
        """

        url = "/v1/management/user_groups"

        return self._get_request(url)

    def get_user_group(self, id: str) -> Dict[str, Any]:
        """
        Gets a User Group by ID
        @param id: The ID of the User
        """

        url = f"/v1/management/user_groups/{id}"

        return self._get_request(url)

    def create_user_group(self, group_name: str, member_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Creates a new User Group
        @param group_name: The name of the User Group
        @param member_ids: The ids of the User Group members
        """

        url = "/v1/management/user_groups"

        body = {
            "groupName": group_name,
            "memberIds": member_ids
        }

        return self._post_request(url, body)

    def update_user_group(self, id: str, group_name: Optional[str] = None, member_ids: Optional[List[str]] = None) -> \
            Dict[str, Any]:
        """
        Updates a User Group
        @param id: The ID of the User Group
        @param group_name: The name of the User Group
        @param member_ids: The ids of the User Group members
        """

        url = f"/v1/management/user_groups/{id}"

        body = {
            "groupName": group_name,
            "memberIds": member_ids
        }

        return self._put_request(url, body)

    def delete_user_group(self, id: str) -> None:
        """
        Deletes a User Group
        @param id: The ID of the User Group
        """

        url = f"/v1/management/user_groups/{id}"

        return self._delete_request(url)

    def get_console_users(self) -> List[Dict[str, Any]]:
        """
        Gets all Console Users for your tenant
        """

        url = "/v1/management/users"

        return self._get_request(url)

    def get_api_users(self) -> List[Dict[str, Any]]:
        """
        Gets all Api Users for your tenant
        """

        url = "/v1/management/api_users"

        return self._get_request(url)

    def create_console_user(self, first_name: str, last_name: str, email: str, role: Role) -> None:
        """
        Create Console User for your tenant
        @param first_name: firstName of the user, example: "Johnny".  Maximum length: 30 chars.
        @param last_name: lastName of the user. Maximum length: 30 chars.
        @param email: email of the user, example: "email@example.com"
        @param role: role of the user, for example: "ADMIN"
        """

        url = "/v1/management/users"

        body = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "role": role
        }

        return self._post_request(url, body)

    def create_api_user(self, name: str, role: Role, csr_pem: str, co_signer_setup: Optional[str] = None, co_signer_setup_is_first_user: Optional[bool] = False) -> None:
        """
        Create Api User for your tenant
        @param role: role of the user, for example: "ADMIN"
        @param name: name of the api user, example: "Johnny The Api".  Maximum length: 30 chars.
        @param csr_pem: generate .csr file and provide its string content here, example:  "-----BEGIN CERTIFICATE REQUEST-----aaa-----END CERTIFICATE REQUEST-----"
        You can find more info about csrPem and how to create it here: https://developers.fireblocks.com/docs/quickstart
        @param co_signer_setup: your cosigner, for example: "SGX_MACHINE", read more: https://developers.fireblocks.com/docs/quickstart
        @param co_signer_setup_is_first_user: [SGX server enabled only] If you are the first user to be configured on this SGX-enabled Co-Signer server, this has to be true
        """

        url = "/v1/management/api_users"

        body = {
            "role": role,
            "name": name,
            "csrPem": csr_pem,
            "coSignerSetup": co_signer_setup,
            "coSignerSetupIsFirstUser": co_signer_setup_is_first_user
        }

        return self._post_request(url, body)

    def reset_device_request(self, id: str) -> None:
        """
        Re-enroll Mobile Device of a user in your tenant
        @param id: userId of the user to reset device
        """

        url = f"/v1/management/users/{id}/reset_device"

        return self._post_request(url)

    def get_whitelisted_ip_addresses(self, id: str) ->  Dict[str, Any]:
        """
        Get whitelisted addresses of api user in your tenant
        @param id: userId of the user
        """

        url = f"/v1/management/api_users/{id}/whitelist_ip_addresses"

        return self._get_request(url)

    def get_off_exchanges(self):
        """
        Get your connected off exchanges virtual accounts
        """
        url = f"/v1/off_exchange_accounts"

        return self._get_request(url)

    def get_audit_logs(self, time_period: TimePeriod = TimePeriod.DAY):
        """
        Get audit logs
        :param time_period: The last time period to fetch audit logs
        """

        url = "/v1/audits"

        return self._get_request(url, query_params={"timePeriod": time_period.value})
        
    def get_paginated_audit_logs(self, time_period: TimePeriod = TimePeriod.DAY, cursor = None):
        """
        Get paginated audit logs
        :param time_period: The last time period to fetch audit logs
        :param cursor: The next id to fetch audit logs from
        """
        url = "/v1/management/audit_logs"
        params = {}

        if cursor:
            params["cursor"] = cursor

        if time_period:
            params["timePeriod"] = time_period.value

        return self._get_request(url, query_params=params)

    def get_off_exchange_by_id(self, off_exchange_id):
        """
        Get your connected off exchange by it's ID
        :param off_exchange_id: ID of the off exchange virtual account
        :return: off exchange entity
        """

        url = f"/v1/off_exchange_accounts/{off_exchange_id}"

        return self._get_request(url)

    def settle_off_exchange_by_id(self, off_exchange_id, idempotency_key=None):
        """
        Create a settle request to your off exchange by it's ID
        :param off_exchange_id: ID of the off exchange virtual account
        :param idempotency_key
        """

        url = f"/v1/off_exchanges/{off_exchange_id}/settle"

        return self._post_request(url, {}, idempotency_key)

    def set_fee_payer_configuration(
            self, base_asset, fee_payer_account_id, idempotency_key=None
    ):
        """
        Setting fee payer configuration for base asset
        :param base_asset: ID of the base asset you want to configure fee payer for (for example: SOL)
        :param fee_payer_account_id: ID of the vault account you want your fee to be paid from
        :param idempotency_key
        """

        url = f"/v1/fee_payer/{base_asset}"

        body = {"feePayerAccountId": fee_payer_account_id}

        return self._post_request(url, body, idempotency_key)

    def get_fee_payer_configuration(self, base_asset):
        """
        Get fee payer configuration for base asset
        :param base_asset: ID of the base asset
        :return: the fee payer configuration
        """

        url = f"/v1/fee_payer/{base_asset}"

        return self._get_request(url)

    def remove_fee_payer_configuration(self, base_asset):
        """
        Delete fee payer configuration for base asset
        :param base_asset: ID of the base asset
        """
        url = f"/v1/fee_payer/{base_asset}"

        return self._delete_request(url)

    def get_web3_connections(
            self, pageCursor=None, pageSize=None, sort=None, filter=None, order=None
    ):
        """
        Get all signer connections of the current user
        :return: Array of sessions
        """

        method_param = locals()
        url = "/v1/connections"
        optional_params = ["pageCursor", "pageSize", "sort", "filter", "order"]

        query_params = {
            param: method_param.get(param)
            for param in optional_params
            if method_param.get(param)
        }

        if query_params:
            url = url + "?" + urllib.parse.urlencode(query_params)

        return self._get_request(url)

    def create_web3_connection(
            self,
            vault_account_id: str,
            uri: str,
            chain_ids: List[str],
            fee_level: str = "MEDIUM",
            idempotency_key: str = None,
    ):
        """
        Initiate a new signer connection
        :param vault_account_id: The id of the requested account
        :param uri: Wallet Connect uri provided by the dApp
        :param chain_ids: A list of chain ids to be used by the connection
        :param fee_level: The fee level of the dropping transaction (HIGH, MEDIUM, LOW)
        :param idempotency_key: Idempotency key
        :return: The created session's ID and its metadata
        """

        url = "/v1/connections/wc"

        payload = {
            "vaultAccountId": int(vault_account_id),
            "feeLevel": fee_level,
            "uri": uri,
            "chainIds": chain_ids,
        }

        return self._post_request(url, payload, idempotency_key)

    def submit_web3_connection(self, session_id: str, approve: bool):
        """
        Approve or Reject the initiated connection
        :param session_id: The ID of the session
        :param approve: Whether you approve the connection or not
        """

        url = f"/v1/connections/wc/{session_id}"

        body = {"approve": approve}

        return self._put_request(url, body)

    def remove_web3_connection(self, session_id: str):
        """
        Remove an existing connection
        :param session_id: The ID of the session
        """

        url = f"/v1/connections/wc/{session_id}"

        return self._delete_request(url)

    def get_active_policy(self):
        """
        Get active policy (TAP) [BETA]
        """

        url = "/v1/tap/active_policy"

        return self._get_request(url)

    def get_draft(self):
        """
        Get draft policy (TAP) [BETA]
        """

        url = "/v1/tap/draft"

        return self._get_request(url)

    def update_draft(self, rules: List[PolicyRule]):
        """
        Update draft policy (TAP) [BETA]
        @param rules: list of policy rules
        """

        url = "/v1/tap/draft"
        body = {}

        if rules is not None and isinstance(rules, list):
            if any([not isinstance(x, PolicyRule) for x in rules]):
                raise FireblocksApiException("Expected rules of type List[PolicyRule]")
            body['rules'] = [rule.to_dict() for rule in rules]

        return self._put_request(url, body)

    def publish_draft(self, draft_id: str):
        """
        Publish draft policy (TAP) [BETA]
        """

        url = "/v1/tap/draft"

        body = {
            "draftId": draft_id
        }

        return self._post_request(url, body)

    def publish_policy_rules(self, rules: List[PolicyRule]):
        """
        Publish policy rules (TAP) [BETA]
        @param rules: list of rules
        """

        url = "/v1/tap/publish"
        body = {}

        if rules is not None and isinstance(rules, list):
            if any([not isinstance(x, PolicyRule) for x in rules]):
                raise FireblocksApiException("Expected rules of type List[PolicyRule]")
            body['rules'] = [rule.to_dict() for rule in rules]

        return self._post_request(url, body)

    def get_smart_transfer_tickets(self, paged_smart_transfer_request_filters: GetSmartTransferFilters):
        """Gets a page of smart transfer for your tenant according to filters given
        Args:
            paged_smart_transfer_request_filters (object, optional): Possible filters to apply for request
        """

        url = "/v1/smart-transfers"

        params = {}

        if paged_smart_transfer_request_filters.query is not None:
            params['q'] = paged_smart_transfer_request_filters.query

        if paged_smart_transfer_request_filters.statuses is not None:
            params['statuses'] = paged_smart_transfer_request_filters.statuses

        if paged_smart_transfer_request_filters.network_id is not None:
            params['networkId'] = paged_smart_transfer_request_filters.network_id

        if paged_smart_transfer_request_filters.created_by_me is not None:
            params['createdByMe'] = bool(paged_smart_transfer_request_filters.created_by_me)

        if paged_smart_transfer_request_filters.expires_after is not None:
            params['expiresAfter'] = paged_smart_transfer_request_filters.expires_after

        if paged_smart_transfer_request_filters.expires_before is not None:
            params['expiresBefore'] = paged_smart_transfer_request_filters.expires_before

        if paged_smart_transfer_request_filters.ticket_type is not None:
            params['type'] = paged_smart_transfer_request_filters.ticket_type

        if paged_smart_transfer_request_filters.external_ref_id is not None:
            params['externalRefId'] = paged_smart_transfer_request_filters.external_ref_id

        if paged_smart_transfer_request_filters.after is not None:
            params['after'] = paged_smart_transfer_request_filters.after

        if paged_smart_transfer_request_filters.limit is not None:
            params['limit'] = int(paged_smart_transfer_request_filters.limit)

        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        return self._get_request(url)

    def create_smart_transfer_ticket(self, ticket_type: str, created_by_network_id: str, terms=None,
                                     expires_in: Optional[int] = None, submit: bool = True, note: Optional[str] = None,
                                     external_ref_id: Optional[str] = None, idempotency_key: str = None):
        """Creates new Smart Transfer ticket
        Args:
            ticket_type (str): Type of the ticket (ASYNC)
            created_by_network_id (str): NetworkId that is used for ticket creation
            expires_in (int): Ticket expiration in hours. Optional
            submit (bool): Flag that will submit ticket immediately - create ticket with OPEN status (ticket will be created in DRAFT otherwise). Optional
            note (str): Note. Optional;
            terms (list, optional): Ticket terms array.
                Each term should have the following keys:
                - 'asset': Asset
                - 'amount': Amount
                - 'fromNetworkId': Source networkId
                - 'toNetworkId': Destination networkId
                Default is an empty list.
            external_ref_id (str): External Reference ID. Optional;
            idempotency_key: Idempotency key
        """

        url = f"/v1/smart-transfers"

        if terms is None:
            terms = []

        payload = {
            "createdByNetworkId": created_by_network_id,
            "type": ticket_type,
            "terms": terms,
            "submit": submit
        }

        if expires_in is not None:
            payload["expiresIn"] = expires_in
        if note is not None:
            payload["note"] = note
        if external_ref_id is not None:
            payload["externalRefId"] = external_ref_id

        return self._post_request(url, payload, idempotency_key)

    def get_smart_transfer_ticket(self, ticket_id: str):
        """Fetch single Smart Transfer ticket
        Args:
            ticket_id (str): ID of the ticket
        """

        url = f"/v1/smart-transfers/{ticket_id}"

        return self._get_request(url)

    def set_smart_transfer_ticket_expires_in(self, ticket_id: str, expires_in: int):
        """Set expiration for ticket.
        Args:
            ticket_id (str): ID of the ticket
            expires_in (int): Expires in (number of hours)
        """

        url = f"/v1/smart-transfers/{ticket_id}/expires-in"

        payload = {
            "expiresIn": expires_in
        }

        return self._put_request(url, payload)

    def set_smart_transfer_ticket_external_ref_id(self, ticket_id: str, external_ref_id: str):
        """Set External Ref. ID for Ticket
        Args:
            ticket_id (str): ID of the ticket
            external_ref_id (str): ticket External Ref. id
        """

        url = f"/v1/smart-transfers/{ticket_id}/external-id"

        payload = {
            "externalRefId": external_ref_id
        }

        return self._put_request(url, payload)

    def submit_smart_transfer_ticket(self, ticket_id: str, expires_in: int):
        """Submit Smart Transfer ticket - change status to OPEN
        Args:
            ticket_id (str): ID of the ticket
            expires_in (int): Expires in (number of hours)
        """

        url = f"/v1/smart-transfers/{ticket_id}/submit"

        payload = {
            "expiresIn": expires_in
        }

        return self._put_request(url, payload)

    def fulfill_smart_transfer_ticket(self, ticket_id: str):
        """Manually fulfill ticket, in case when all terms (legs) are funded manually
        Args:
            ticket_id (str): ID of the ticket
        """

        url = f"/v1/smart-transfers/{ticket_id}/fulfill"

        return self._put_request(url)

    def cancel_smart_transfer_ticket(self, ticket_id: str):
        """Cancel Smart Transfer ticket
        Args:
            ticket_id (str): ID of the ticket
        """

        url = f"/v1/smart-transfers/{ticket_id}/cancel"

        return self._put_request(url)

    def create_smart_transfer_ticket_term(self, ticket_id: str, asset: str, amount, from_network_id: str,
                                          to_network_id: str, idempotency_key: str = None):
        """Create new Smart Transfer ticket term/leg (when ticket in DRAFT)
        Args:
            ticket_id (str): Ticket ID
            asset (str): ID of asset
            amount (double): Amount
            from_network_id (str): Source network id
            to_network_id (str): Destination network id
            idempotency_key (str): Idempotency key
        """

        url = f"/v1/smart-transfers/{ticket_id}/terms"

        payload = {
            "asset": asset,
            "amount": amount,
            "fromNetworkId": from_network_id,
            "toNetworkId": to_network_id,
        }

        return self._post_request(url, payload, idempotency_key)

    def get_smart_transfer_ticket_term(self, ticket_id: str, term_id: str):
        """Gets Smart Transfer ticket term/leg
        Args:
            ticket_id (str): Ticket ID
            term_id (str): Term ID
        """

        url = f"/v1/smart-transfers/{ticket_id}/terms/{term_id}"

        return self._get_request(url)

    def update_smart_transfer_ticket_term(self, ticket_id: str, term_id: str, asset: str, amount, from_network_id: str,
                                          to_network_id: str):
        """Update Smart Transfer ticket term/leg
        Args:
            ticket_id (str): Ticket ID
            term_id (str): Term ID
            asset (str): ID of asset
            amount (double): Amount
            from_network_id (str): Source network id
            to_network_id (str): Destination network id
        """

        url = f"/v1/smart-transfers/{ticket_id}/terms/{term_id}"

        payload = {
            "asset": asset,
            "amount": amount,
            "fromNetworkId": from_network_id,
            "toNetworkId": to_network_id,
        }

        return self._put_request(url, payload)

    def delete_smart_transfer_ticket_term(self, ticket_id: str, term_id: str):
        """Delete Smart Transfer ticket term/leg
        Args:
            ticket_id (str): Ticket ID
            term_id (str): Term ID
        """

        url = f"/v1/smart-transfers/{ticket_id}/terms/{term_id}"

        return self._delete_request(url)

    def fund_smart_transfer_ticket_term(self, ticket_id: str, term_id, asset: str, amount, network_connection_id: str,
                                        source_id: str, source_type: str, fee: Optional[str] = None,
                                        fee_level: Optional[str] = None):
        """Fund Smart Transfer ticket term/leg
        Args:
            ticket_id (str): Ticket ID
            term_id (str): Term ID
            asset (str): ID of asset
            amount (str): String representation of amount ("1.2" e.g.)
            network_connection_id (str): Connection id
            source_id (str): Source id for transaction
            source_type (str, optional): Only gets transactions with given source_type, which should be one of the following:
                VAULT_ACCOUNT, EXCHANGE, FIAT_ACCOUNT
            fee (double, optional): Sathoshi/Latoshi per byte.
            fee_level: The fee level of the dropping transaction (HIGH, MEDIUM, LOW)
        """

        url = f"/v1/smart-transfers/{ticket_id}/terms/{term_id}/fund"

        payload = {
            "asset": asset,
            "amount": amount,
            "networkConnectionId": network_connection_id,
            "srcId": source_id,
            "srcType": source_type,
        }

        if fee is not None:
            payload["fee"] = fee

        if fee_level is not None:
            if fee_level not in FEE_LEVEL:
                raise FireblocksApiException("Got invalid fee level: " + fee_level)
            payload["feeLevel"] = fee_level

        return self._put_request(url, payload)

    def manually_fund_smart_transfer_ticket_term(self, ticket_id: str, term_id, tx_hash: str):
        """Manually fund Smart Transfer ticket term/leg
        Args:
            ticket_id (str): Ticket ID
            term_id (str): Term ID
            tx_hash (str): Transaction hash
        """

        url = f"/v1/smart-transfers/{ticket_id}/terms/{term_id}/manually-fund"

        payload = {
            "txHash": tx_hash,
        }

        return self._put_request(url, payload)

    def set_smart_transfer_user_group_ids(self, user_group_ids):
        """Set Smart Transfer user group ids
        Args:
            user_group_ids (list): List of user groups ids to receive Smart Transfer notifications
        """

        url = "/v1/smart-transfers/settings/user-groups"

        payload = {
            "userGroupIds": user_group_ids,
        }

        return self._post_request(url, payload)

    def get_smart_transfer_user_group_ids(self):
        """Fetch Smart Transfer user group ids that will receive Smart Transfer notifications
        """

        url = "/v1/smart-transfers/settings/user-groups"

        return self._get_request(url)
    
    def get_linked_tokens(self, limit: int = 100, offset: int = 0):
        request_filter = {"limit": limit, "offset": offset}
        return self._get_request("/v1/tokenization/tokens", query_params=request_filter)

    def issue_new_token(self, request: CreateTokenRequest):
        return self._post_request("/v1/tokenization/tokens", request.to_dict())

    def get_linked_token(self, assetId: str):
        return self._get_request(f"/v1/tokenization/tokens/{assetId}")

    def link_token(self, assetId: str):
        return self._put_request(f"/v1/tokenization/tokens/{assetId}/link", {})

    def unlink_token(self, assetId: str):
        return self._delete_request(f"/v1/tokenization/tokens/{assetId}")
    
    def get_contract_templates(self, limit: int = 100, offset: int = 0):
        request_filter = {
            "limit": limit,
            "offset": offset
        }
        return self._get_request("/v1/contract-registry/contracts", query_params=request_filter)

    def upload_contract_template(self, request: ContractUploadRequest):
        return self._post_request("/v1/contract-registry/contracts", request.to_dict())

    def get_contract_template(self, contractId: str):
        return self._get_request(f"/v1/contract-registry/contracts/{contractId}")

    def get_contract_template_constructor(self, contractId: str, with_docs: bool=False):
        return self._get_request(f"/v1/contract-registry/contracts/{contractId}/constructor?withDocs=${with_docs}")

    def delete_contract_template(self, contractId: str):
        return self._delete_request(f"/v1/contract-registry/contracts/{contractId}")

    def deploy_contract(self, contractId: str, request: ContractDeployRequest):
        return self._post_request(f"/v1/contract-registry/contracts/{contractId}/deploy", request.to_dict())
    
    def get_contracts_by_filter(self, templateId: str, blockchainId: str = None):
        return self._get_request(f"/v1/contract-service/contracts?templateId={templateId}&blockchainId={blockchainId}")
    
    def get_contract_by_address(self, blockchainId: str, contractAddress: str):
        return self._get_request(f"/v1/contract-service/contracts/{blockchainId}/{contractAddress}")
    
    def get_contract_abi(self, blockchainId: str, contractAddress: str):
        return self._get_request(f"/v1/contract-service/contracts/{blockchainId}/{contractAddress}/abi")
    
    def read_contract_call_function(self, blockchainId: str, contractAddress: str, request: ReadCallFunction):
        return self._post_request(f"/v1/contract-service/contracts/{blockchainId}/{contractAddress}/function/read", request.to_dict())

    def write_contract_call_function(self, blockchainId: str, contractAddress: str, request: WriteCallFunction):
        return self._post_request(f"/v1/contract-service/contracts/{blockchainId}/{contractAddress}/function/write", request.to_dict())

    def _get_request(self, path, page_mode=False, query_params: Dict = None):
        if query_params:
            path = path + "?" + urllib.parse.urlencode(query_params)
        token = self.token_provider.sign_jwt(path)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.http_session.get(
            self.base_url + path, headers=headers, timeout=self.timeout
        )
        return handle_response(response, page_mode)

    def _delete_request(self, path):
        token = self.token_provider.sign_jwt(path)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.http_session.delete(
            self.base_url + path, headers=headers, timeout=self.timeout
        )
        return handle_response(response)

    def _post_request(self, path, body=None, idempotency_key=None):
        body = body or {}

        token = self.token_provider.sign_jwt(path, body)
        headers = {"Authorization": f"Bearer {token}"}
        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key

        response = self.http_session.post(
            self.base_url + path, headers=headers, json=body, timeout=self.timeout
        )
        return handle_response(response)

    def _put_request(self, path, body=None, query_params=None):
        body = body or {}
        if query_params:
            path = path + "?" + urllib.parse.urlencode(query_params)

        token = self.token_provider.sign_jwt(path, body)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = self.http_session.put(
            self.base_url + path,
            headers=headers,
            data=json.dumps(body),
            timeout=self.timeout,
        )
        return handle_response(response)

    def _patch_request(self, path, body=None):
        body = body or {}

        token = self.token_provider.sign_jwt(path, body)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.http_session.patch(
            self.base_url + path, headers=headers, json=body, timeout=self.timeout
        )
        return handle_response(response)

    @staticmethod
    def _get_user_agent(anonymous_platform):
        user_agent = f"fireblocks-sdk-py/{version('fireblocks_sdk')}"
        if not anonymous_platform:
            user_agent += (
                f" ({platform.system()} {platform.release()}; "
                f"{platform.python_implementation()} {platform.python_version()}; "
                f"{platform.machine()})"
            )
        return user_agent
