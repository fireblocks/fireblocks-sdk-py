import urllib
from operator import attrgetter
from typing import List, Union

from fireblocks_sdk.api_types import PagedVaultAccountsRequestFilters
from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.entities.asset_response import AssetResponse
from fireblocks_sdk.entities.op_success_response import OperationSuccessResponse
from fireblocks_sdk.entities.vault_accounts_filter import VaultAccountsFilter
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.vaults.deposit_address_response import DepositAddressResponse
from fireblocks_sdk.services.vaults.generate_address_response import GenerateAddressResponse
from fireblocks_sdk.services.vaults.vault_account_response import VaultAccountResponse


class VaultsService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    @response_deserializer(VaultAccountResponse)
    def get_vault_accounts(self, filter: Union[VaultAccountsFilter, None] = None) -> List[VaultAccountResponse]:
        """Gets all vault accounts for your tenant

        Args:
            name_prefix (string, optional): Vault account name prefix
            name_suffix (string, optional): Vault account name suffix
            min_amount_threshold (number, optional):  The minimum amount for asset to have in order to be included in the results
            assetId (string, optional): The asset symbol
        """

        url = "/v1/vault/accounts"

        if filter:
            url = url + "?" + filter.serialize()

        return self.connector.get(url).content
        # return [VaultAccountResponse.deserialize(account) for account in response]

    def get_vault_accounts_with_page_info(self, paged_vault_accounts_request_filters: PagedVaultAccountsRequestFilters):
        """Gets a page of vault accounts for your tenant according to filters given

        Args:
            paged_vault_accounts_request_filters (object, optional): Possible filters to apply for request
        """

        url = f"/v1/vault/accounts_paged"
        name_prefix, name_suffix, min_amount_threshold, asset_id, order_by, limit, before, after = \
            attrgetter('name_prefix', 'name_suffix', 'min_amount_threshold', 'asset_id',
                       'order_by', 'limit', 'before', 'after')(paged_vault_accounts_request_filters)

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

        return self.connector.get(url)

    @response_deserializer(VaultAccountResponse)
    def get_vault_account(self, vault_account_id: str) -> VaultAccountResponse:
        """Deprecated - Replaced by get_vault_account_by_id
        Args:
            vault_account_id (string): The id of the requested account
        """

        return self.connector.get(f"/v1/vault/accounts/{vault_account_id}").content

    @response_deserializer(VaultAccountResponse)
    def get_vault_account_by_id(self, vault_account_id: str) -> VaultAccountResponse:
        """Gets a single vault account
        Args:
            vault_account_id (string): The id of the requested account
        """

        return self.connector.get(f"/v1/vault/accounts/{vault_account_id}").content

    @response_deserializer(AssetResponse)
    def get_vault_account_asset(self, vault_account_id: str, asset_id: str) -> AssetResponse:
        """Gets a single vault account asset
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self.connector.get(f"/v1/vault/accounts/{vault_account_id}/{asset_id}").content

    @response_deserializer(AssetResponse)
    def refresh_vault_asset_balance(self, vault_account_id: str, asset_id: str,
                                    idempotency_key: Union[str, None] = None) -> AssetResponse:
        """Gets a single vault account asset after forcing refresh from the blockchain
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self.connector.post(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/balance", {}, idempotency_key).content

    @response_deserializer(DepositAddressResponse)
    def get_deposit_addresses(self, vault_account_id: str, asset_id: str) -> List[DepositAddressResponse]:
        """Gets deposit addresses for an asset in a vault account
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self.connector.get(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses").content

    @response_deserializer(DepositAddressResponse)
    def get_unspent_inputs(self, vault_account_id: str, asset_id: str) -> List[DepositAddressResponse]:
        """Gets utxo list for an asset in a vault account
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (like BTC, DASH and utxo based assets)
        """

        return self.connector.get(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/unspent_inputs").content

    @response_deserializer(GenerateAddressResponse)
    def generate_new_address(self, vault_account_id: str, asset_id: str, description: Union[str, None] = None,
                             customer_ref_id: Union[str, None] = None,
                             idempotency_key: Union[str, None] = None) -> GenerateAddressResponse:
        """Generates a new address for an asset in a vault account

        Args:
            vault_account_id (string): The vault account ID
            asset_id (string): The ID of the asset for which to generate the deposit address
            description (string, optional): A description for the new address
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self.connector.post(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses",
                                   {"description": description or '',
                                    "customerRefId": customer_ref_id or ''},
                                   idempotency_key).content

    @response_deserializer(GenerateAddressResponse)
    def set_address_description(self, vault_account_id: str, asset_id: str, address: str, tag: Union[str, None] = None,
                                description: Union[str, None] = None) -> GenerateAddressResponse:
        """Sets the description of an existing address

        Args:
            vault_account_id (string): The vault account ID
            asset_id (string): The ID of the asset
            address (string): The address for which to set the set_address_description
            tag (string, optional): The XRP tag, or EOS memo, for which to set the description
            description (string, optional): The description to set, or none for no description
        """
        if tag:
            return self.connector.put(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}:{tag}",
                                      {"description": description or ''}).content
        else:
            return self.connector.put(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}",
                                      {"description": description or ''}).content

    @response_deserializer(VaultAccountResponse)
    def create_vault_account(self, name: str, hidden_on_ui: bool = False, customer_ref_id: Union[str, None] = None,
                             auto_fuel: bool = False, idempotency_key: Union[str, None] = None) -> VaultAccountResponse:
        """Creates a new vault account.

        Args:
            name (str): A name for the new vault account
            hidden_on_ui (boolean): Specifies whether the vault account is hidden from the web console, false by default
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """
        body = {
            "name": name,
            "hiddenOnUI": hidden_on_ui,
            "autoFuel": auto_fuel
        }

        if customer_ref_id:
            body["customerRefId"] = customer_ref_id

        return self.connector.post("/v1/vault/accounts", body, idempotency_key).content

    @response_deserializer(OperationSuccessResponse)
    def hide_vault_account(self, vault_account_id: str, idempotency_key=None) -> OperationSuccessResponse:
        """Hides the vault account from being visible in the web console

        Args:
            vault_account_id (str): The vault account Id
            idempotency_key (str, optional)
        """
        return self.connector.post(f"/v1/vault/accounts/{vault_account_id}/hide",
                                   idempotency_key=idempotency_key).content

    @response_deserializer(OperationSuccessResponse)
    def unhide_vault_account(self, vault_account_id: str,
                             idempotency_key: Union[str, None] = None) -> OperationSuccessResponse:
        """Returns the vault account to being visible in the web console

        Args:
            vault_account_id (str): The vault account Id
            idempotency_key (str, optional)
        """
        return self.connector.post(f"/v1/vault/accounts/{vault_account_id}/unhide",
                                   idempotency_key=idempotency_key).content

    @response_deserializer(VaultAccountResponse)
    def update_vault_account(self, vault_account_id: str, name: str) -> VaultAccountResponse:
        """Updates a vault account.

        Args:
            vault_account_id (str): The vault account Id
            name (str): A new name for the vault account
        """
        body = {
            "name": name,
        }

        return self.connector.put(f"/v1/vault/accounts/{vault_account_id}", body).content

    def create_vault_asset(self, vault_account_id: str, asset_id: str, idempotency_key: Union[str, None] = None):
        """Creates a new asset within an existing vault account

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            idempotency_key (str, optional)
        """

        return self.connector.post(f"/v1/vault/accounts/{vault_account_id}/{asset_id}", idempotency_key=idempotency_key)

    def activate_vault_asset(self, vault_account_id: str, asset_id: str, idempotency_key: Union[str, None] = None):
        """Retry to create a vault asset for a vault asset that failed

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            idempotency_key (str, optional)
        """

        return self.connector.post(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/activate",
                                   idempotency_key=idempotency_key)

    def set_vault_account_customer_ref_id(self, vault_account_id: str, customer_ref_id: str,
                                          idempotency_key: Union[str, None] = None):
        """Sets an AML/KYT customer reference ID for the vault account

        Args:
            vault_account_id (str): The vault account Id
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self.connector.post(f"/v1/vault/accounts/{vault_account_id}/set_customer_ref_id",
                                   {"customerRefId": customer_ref_id or ''}, idempotency_key)

    @response_deserializer(OperationSuccessResponse)
    def set_vault_account_customer_ref_id_for_address(self, vault_account_id: str, asset_id: str, address: str,
                                                      customer_ref_id: Union[str, None] = None,
                                                      idempotency_key: Union[
                                                          str, None] = None) -> OperationSuccessResponse:
        """Sets an AML/KYT customer reference ID for the given address

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            address (string): The address for which to set the customer reference id
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self.connector.post(
            f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}/set_customer_ref_id",
            {"customerRefId": customer_ref_id or ''}, idempotency_key).content

    def get_public_key_info_for_vault_account(self, asset_id: str, vault_account_id: str, change: int,
                                              address_index: int, compressed: Union[bool, None] = None):
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

        return self.connector.get(url)

    def allocate_funds_to_private_ledger(self, vault_account_id: str, asset: str, allocation_id: str, amount: str,
                                         treat_as_gross_amount: Union[bool, None] = None,
                                         idempotency_key: Union[str, None] = None):
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

        return self.connector.post(url, {"allocationId": allocation_id, "amount": amount,
                                         "treatAsGrossAmount": treat_as_gross_amount or False}, idempotency_key)

    def deallocate_funds_from_private_ledger(self, vault_account_id: str, asset: str, allocation_id: str, amount: str,
                                             idempotency_key: Union[str, None] = None):
        """deallocate funds from a private ledger to your default balance

        Args:
            vault_account_id (string)
            asset (string)
            allocation_id (string)
            amount (string)
            idempotency_key (string, optional)
        """

        url = f"/v1/vault/accounts/{vault_account_id}/{asset}/release_allocation"

        return self.connector.post(url, {"allocationId": allocation_id, "amount": amount}, idempotency_key)

    def get_max_spendable_amount(self, vault_account_id: str, asset_id: str, manual_signing: bool = False):
        """Get max spendable amount per asset and vault.

        Args:
            vault_account_id (str): The vault account Id.
            asset_id (str): Asset id.
            manual_signing (boolean, optional): False by default.
        """
        url = f"/v1/vault/accounts/{vault_account_id}/{asset_id}/max_spendable_amount?manual_signing={manual_signing}"

        return self.connector.get(url)

    def set_auto_fuel(self, vault_account_id: str, auto_fuel: bool, idempotency_key=None):
        """Sets autoFuel to true/false for a vault account

        Args:
            vault_account_id (str): The vault account Id
            auto_fuel (boolean): The new value for the autoFuel flag
            idempotency_key (str, optional)
        """
        body = {
            "autoFuel": auto_fuel
        }

        return self.connector.post(f"/v1/vault/accounts/{vault_account_id}/set_auto_fuel", body, idempotency_key)

    def get_public_key_info(self, algorithm: str, derivation_path: str, compressed=None):
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
        return self.connector.get(url)

    @response_deserializer(AssetResponse)
    def get_vault_assets_balance(self, account_name_prefix: Union[str, None] = None,
                                 account_name_suffix: Union[str, None] = None) -> List[AssetResponse]:
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

        return self.connector.get(url).content

    @response_deserializer(AssetResponse)
    def get_vault_balance_by_asset(self, asset_id: Union[str, None] = None) -> AssetResponse:
        """Gets vault accumulated balance by asset

         Args:
            asset_id (str, optional): The asset symbol (e.g BTC, ETH)
        """
        url = f"/v1/vault/assets"

        if asset_id:
            url += f"/{asset_id}"

        return self.connector.get(url).content
