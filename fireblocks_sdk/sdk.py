import requests
import urllib
import json

from .sdk_token_provider import SdkTokenProvider
from .api_types import FireblocksApiException, TRANSACTION_TYPES, TRANSACTION_STATUS_TYPES, PEER_TYPES, TransferPeerPath, DestinationTransferPeerPath, TransferTicketTerm, TRANSACTION_TRANSFER

class FireblocksSDK(object):

    def __init__(self, private_key, api_key, api_base_url="https://api.fireblocks.io"):
        """Creates a new Fireblocks API Client.

        Args:
            private_key (str): A string representation of your private key (in PEM format)
            api_key (str): Your api key. This is a uuid you received from Fireblocks
            base_url (str): The fireblocks server URL. Leave empty to use the default server
        """
        self.private_key = private_key
        self.api_key = api_key
        self.base_url = api_base_url
        self.token_provider = SdkTokenProvider(private_key, api_key)

    def get_supported_assets(self):
        """Gets all assets that are currently supported by Fireblocks"""

        return self._get_request("/v1/supported_assets")

    def get_vault_accounts(self):
        """Gets all vault accounts for your tenant"""

        return self._get_request("/v1/vault/accounts")

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

    def get_deposit_addresses(self, vault_account_id, asset_id):
        """Gets deposit addresses for an asset in a vault account
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The symbol of the requested asset (e.g BTC, ETH)
        """

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses")

    def generate_new_address(self, vault_account_id, asset_id, description=None, customer_ref_id=None):
        """Generates a new address for an asset in a vault account

        Args:
            vault_account_id (string): The vault account ID
            asset_id (string): The ID of the asset for which to generate the deposit address
            description (string, optional): A description for the new address
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses", { "description": description or '', "customerRefId": customer_ref_id or ''})

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
            return self._put_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}:{tag}", { "description": description or ''})
        else:
            return self._put_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}", { "description": description or ''})

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

    def transfer_to_subaccount(self, exchange_account_id, subaccount_id, asset_id, amount):
        """Transfer to a subaccount from a main exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            subaccount_id (string): The ID of the subaccount in the exchange
            asset_id (string): The asset to transfer
            amount (double): The amount to transfer
        """
        body = {
            "subaccountId": subaccount_id,
            "amount": amount
        }

        return self._post_request(f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}/transfer_to_subaccount", body)

    def transfer_from_subaccount(self, exchange_account_id, subaccount_id, asset_id, amount):
        """Transfer from a subaccount to a main exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            subaccount_id (string): The ID of the subaccount in the exchange
            asset_id (string): The asset to transfer
            amount (double): The amount to transfer
        """
        body = {
            "subaccountId": subaccount_id,
            "amount": amount
        }

        return self._post_request(f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}/transfer_from_subaccount", body)

    def get_fiat_accounts(self):
        """Gets all fiat accounts for your tenant"""

        return self._get_request("/v1/fiat_accounts")

    def get_fiat_account_by_id(self, account_id):
        """Gets a single fiat account by ID

        Args:
            account_id (string): The fiat account ID
        """

        return self._get_request(f"/v1/fiat_accounts/{account_id}")

    def redeem_to_linked_dda(self, account_id, amount):
        """Redeem from a fiat account to a linked DDA

        Args:
            account_id (string): The fiat account ID in Fireblocks
            amount (double): The amount to transfer
        """
        body = {
            "amount": amount,
        }

        return self._post_request(f"/v1/fiat_accounts/{account_id}/redeem_to_linked_dda", body)

    def deposit_from_linked_dda(self, account_id, amount):
        """Deposit to a fiat account from a linked DDA

        Args:
            account_id (string): The fiat account ID in Fireblocks
            amount (double): The amount to transfer
        """
        body = {
            "amount": amount,
        }

        return self._post_request(f"/v1/fiat_accounts/{account_id}/deposit_from_linked_dda", body)

    def get_transactions(self, before=0, after=0, status=None, limit=None, order_by=None, txhash=None,
                         assets=None, source_type=None, source_id=None, dest_type=None, dest_id=None):
        """Gets a list of transactions matching the given filter

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
        if  txhash:
            params['txHash'] = txhash
        if assets:
            params['assets'] = assets
        if source_type:
            params['sourcetype'] = source_type
        if source_id:
            params['sourceId'] = source_id
        if dest_type:
            params['destType'] = dest_type
        if dest_id:
            params['destId'] = dest_id

        if params:
            path = path + "?" + urllib.parse.urlencode(params)

        return self._get_request(path)

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


    def get_fee_for_asset(self, asset_id):
        """Gets the estimated fees for an asset

        Args:
            asset_id (str): The asset symbol (e.g BTC, ETH)
        """

        return self._get_request(f"/v1/estimate_network_fee?assetId={asset_id}")

    def estimate_fee_for_transaction(self, asset_id, amount, source, destination=None , tx_type=TRANSACTION_TRANSFER):
        """Estimates transaction fee

        Args:
            asset_id (str): The asset symbol (e.g BTC, ETH)
            source (TransferPeerPath): The transaction source
            destination (DestinationTransferPeerPath, optional): The transfer destination.
            amount (str): The amount
            tx_type (str, optional): Transaction type: either TRANSFER, MINT, BURN, TRANSACTION_SUPPLY_TO_COMPOUND or TRANSACTION_REDEEM_FROM_COMPOUND. Default is TRANSFER.
        """

        if tx_type not in TRANSACTION_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + tx_type)

        if not isinstance(source, TransferPeerPath):
            raise FireblocksApiException("Expected transaction source of type TransferPeerPath, but got type: " + type(source))

        body = {
            "assetId": asset_id,
            "amount": amount,
            "source": source.__dict__,
            "operation": tx_type
        }

        if destination:
            if not isinstance(destination, (TransferPeerPath, DestinationTransferPeerPath)):
                raise FireblocksApiException("Expected transaction fee estimation destination of type DestinationTransferPeerPath or TransferPeerPath, but got type: " + type(destination))
            body["destination"] = destination.__dict__

        return self._post_request("/v1/transactions/estimate_fee", body)

    def cancel_transaction_by_id(self, txid):
        """Cancels the selected transaction

        Args:
            txid (str): The transaction id to cancel
        """

        return self._post_request(f"/v1/transactions/{txid}/cancel")

    def drop_transaction(self, txid, fee_level=None):
        """Drops the selected transaction from the blockchain by replacing it with a 0 ETH transaction to itself

        Args:
            txid (str): The transaction id to drop
            fee_level (str): The fee level of the dropping transaction 
        """
        body = {}

        if fee_level:
            body["feeLevel"] = fee_level

        return self._post_request(f"/v1/transactions/{txid}/drop", body)

    def create_vault_account(self, name, hiddenOnUI=False, customer_ref_id=None):
        """Creates a new vault account.

        Args:
            name (str): A name for the new vault account
            hiddenOnUI (boolean): Specifies whether the vault account is hidden from the web console, false by default
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
        """
        body = {
            "name": name,
            "hiddenOnUI": hiddenOnUI
        }

        if customer_ref_id:
            body["customerRefId"] = customer_ref_id

        return self._post_request("/v1/vault/accounts", body)

    def hide_vault_account(self, vault_account_id):
        """Hides the vault account from being visible in the web console

        Args:
            vault_account_id (str): The vault account Id
        """
        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/hide")

    def unhide_vault_account(self, vault_account_id):
        """Returns the vault account to being visible in the web console

        Args:
            vault_account_id (str): The vault account Id
        """
        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/unhide")
    
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

    def create_vault_asset(self, vault_account_id, asset_id):
        """Creates a new asset within an existing vault account

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}")

    def set_vault_account_customer_ref_id(self, vault_account_id, customer_ref_id):
        """Sets an AML/KYT customer reference ID for the vault account

        Args:
            vault_account_id (str): The vault account Id
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/set_customer_ref_id", {"customerRefId": customer_ref_id or ''})

    def set_vault_account_customer_ref_id_for_address(self, vault_account_id, asset_id, address, customer_ref_id=None):
        """Sets an AML/KYT customer reference ID for the given address

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            address (string): The address for which to set the customer reference id
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
        """

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses/{address}/set_customer_ref_id", {"customerRefId": customer_ref_id or ''})


    def create_external_wallet(self, name, customer_ref_id):
        """Creates a new external wallet

        Args:
            name (str): A name for the new external wallet
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
        """

        return self._post_request("/v1/external_wallets", {"name": name, "customerRefId": customer_ref_id or ''})

    def create_internal_wallet(self, name, customer_ref_id=None):
        """Creates a new internal wallet

        Args:
            name (str): A name for the new internal wallet
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
        """

        return self._post_request("/v1/internal_wallets", {"name": name, "customerRefId": customer_ref_id or ''})

    def create_external_wallet_asset(self, wallet_id, asset_id, address, tag=None):
        """Creates a new asset within an exiting external wallet

        Args:
            wallet_id (str): The wallet id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            address (str): The wallet address
            tag (str, optional): (for ripple only) The ripple account tag
        """

        body = {"address": address}
        if tag:
            body["tag"] = tag

        return self._post_request(
            f"/v1/external_wallets/{wallet_id}/{asset_id}", body
            )

    def create_internal_wallet_asset(self, wallet_id, asset_id, address, tag=None):
        """Creates a new asset within an exiting internal wallet

        Args:
            wallet_id (str): The wallet id
            asset_id (str): The symbol of the asset to add (e.g BTC, ETH)
            address (str): The wallet address
            tag (str, optional): (for ripple only) The ripple account tag
        """

        body = {"address": address}
        if tag:
            body["tag"] = tag

        return self._post_request(
            f"/v1/internal_wallets/{wallet_id}/{asset_id}", body
            )


    def create_transaction(self, asset_id, amount, source, destination=None , fee=None, gas_price=None, wait_for_status=False, tx_type=TRANSACTION_TRANSFER, note=None, cpu_staking=None, network_staking=None, auto_staking=None, customer_ref_id=None, replace_tx_by_hash=None, extra_parameters=None):
        """Creates a new transaction

        Args:
            asset_id (str): The asset symbol (e.g BTC, ETH)
            source (TransferPeerPath): The transfer source
            destination (DestinationTransferPeerPath, optional): The transfer destination. Leave empty (None) if the transaction has no destination
            amount (double): The amount
            fee (double, optional): Sathoshi/Latoshi per byte.
            gas_price (number, optional): gasPrice for ETH and ERC-20 transactions.
            wait_for_status (bool, optional): If true, waits for transaction status. Default is false.
            tx_type (str, optional): Transaction type: either TRANSFER, MINT, BURN, TRANSACTION_SUPPLY_TO_COMPOUND or TRANSACTION_REDEEM_FROM_COMPOUND. Default is TRANSFER.
            note (str, optional): A custome note that can be associated with the transaction.
            cpu_staking (number, optional): Cpu stake for EOS transfer.
            network_staking (number, optional): Network stake for EOS transfer.
            auto_staking: (boolean, optional): Auto stake for EOS transfer. Staking will be managed by fireblocks.
            customer_ref_id (string, optional): The ID for AML providers to associate the owner of funds with transactions
            extra_parameters (object, optional)
        """

        if tx_type not in TRANSACTION_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + tx_type)

        if not isinstance(source, TransferPeerPath):
            raise FireblocksApiException("Expected transaction source of type TransferPeerPath, but got type: " + type(source))

        body = {
            "assetId": asset_id,
            "amount": amount,
            "source": source.__dict__,
            "waitForStatus": wait_for_status,
            "operation": tx_type
        }

        if fee:
            body["fee"] = fee

        if gas_price:
            body["gasPrice"] = gas_price

        if note:
            body["note"] = note

        if destination:
            if not isinstance(destination, (TransferPeerPath, DestinationTransferPeerPath)):
                raise FireblocksApiException("Expected transaction destination of type DestinationTransferPeerPath or TransferPeerPath, but got type: " + type(destination))
            body["destination"] = destination.__dict__
            
        if cpu_staking:
            body["cpuStaking"] = cpu_staking
            
        if network_staking:
            body["networkStaking"] = network_staking
            
        if auto_staking:
            body["autoStaking"] = auto_staking
        
        if customer_ref_id:
            body["customerRefId"] = customer_ref_id
        
        if replace_tx_by_hash:
            body["replaceTxByHash"] = replace_tx_by_hash

        if extra_parameters:
            body["extraParameters"] = extra_parameters
            

        return self._post_request("/v1/transactions", body)

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

    def set_customer_ref_id_for_internal_wallet(self, wallet_id, customer_ref_id=None):
        """Sets an AML/KYT customer reference ID for the specific internal wallet

        Args:
            wallet_id (string): The external wallet ID
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
        """

        return self._post_request(f"/v1/internal_wallets/{wallet_id}/set_customer_ref_id", {"customerRefId": customer_ref_id or ''})

    def set_customer_ref_id_for_external_wallet(self, wallet_id, customer_ref_id=None):
        """Sets an AML/KYT customer reference ID for the specific external wallet

        Args:
            wallet_id (string): The external wallet ID
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
        """

        return self._post_request(f"/v1/external_wallets/{wallet_id}/set_customer_ref_id", {"customerRefId": customer_ref_id or ''})

    def get_transfer_tickets(self):
        """Gets all transfer tickets of your tenant"""

        return self._get_request("/v1/transfer_tickets")

    def create_transfer_ticket(self, terms, external_ticket_id=None, description=None):
        """Creates a new transfer ticket

        Args:
            terms (list of TransferTicketTerm objects): The list of TransferTicketTerm
            external_ticket_id (str, optional): The ID for of the transfer ticket on customer's platform
            description (str, optional): A description for the new ticket
        """

        body = {}

        if external_ticket_id:
            body["externalTicketId"] = external_ticket_id

        if description:
            body["description"] = description

        if any([not isinstance(x, TransferTicketTerm) for x in terms]):
            raise FireblocksApiException("Expected Tranfer Assist ticket's term of type TranferTicketTerm")

        body['terms'] = [term.__dict__ for term in terms]

        return self._post_request(f"/v1/transfer_tickets", body)

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

    def cancel_transfer_ticket(self, ticket_id):
        """Cancel a transfer ticket

        Args:
            ticket_id (str): The ID of the transfer ticket to cancel
        """

        return self._post_request(f"/v1/transfer_tickets/{ticket_id}/cancel")

    def execute_ticket_term(self, ticket_id, term_id, source=None):
        """Initiate a transfer ticket transaction

        Args:
            ticket_id (str): The ID of the transfer ticket
            term_id (str): The ID of the term within the transfer ticket
            source (TransferPeerPath): JSON object of the source of the transaction. The network connection's vault account by default
        """

        body = {}

        if source:
            if not isinstance(source, TransferPeerPath):
                raise FireblocksApiException("Expected ticket term source Of type TransferPeerPath, but got type: " + type(source))
            body["source"] = source.__dict__


        return self._post_request(f"/v1/transfer_tickets/{ticket_id}/{term_id}/transfer", body)
    
    def set_confirmation_threshold_for_txid(self, txid, required_confirmations_number):
        """Set the required number of confirmations for transaction
        
        Args:
            txid (str): The transaction id
            required_confirmations_Number (number): Required confirmation threshold fot the txid
        """
        
        body = {
            "numOfConfirmations": required_confirmations_number
        }
        
        return self._post_request(f"/v1/transactions/{txid}/set_confirmation_threshold", body)
    
    def set_confirmation_threshold_for_txhash(self, txhash, required_confirmations_number):
        """Set the required number of confirmations for transaction by txhash
        
        Args:
            txhash (str): The transaction hash 
            required_confirmations_Number (number): Required confirmation threshold fot the txhash
        """
        
        body = {
            "numOfConfirmations": required_confirmations_number
        }
        
        return self._post_request(f"/v1/txHash/{txhash}/set_confirmation_threshold", body)
    
    def get_public_key_info(self, algorithm, derivation_path, compressed=None ):
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
            url += f"&derivationPath={derivation_path}"
        if compressed:
            url += f"&compressed={compressed}"
            
        return self._get_request(url)
    
    def get_public_key_info_for_vault_account(self, asset_id, vault_account_id, change, address_index, compressed=None ):
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
    
    def get_gas_station_info(self):
        "Get configuration and status of the Gas Station account"
        
        url = f"/v1/gas_station"

        return self._get_request(url)
    
    def set_gas_station_configuration(self, gas_threshold, gas_cap, max_gas_price):
        """Set configuration of the Gas Station account
        
        Args:
            gasThreshold (str)
            gasCap (str)
            maxGasPrice (str, optional)
        """
        
        url = f"/v1/gas_station/configuration"
        
        body = {
            "gasThreshold": gas_threshold,
            "gasCap": gas_cap,
            "maxGasPrice": max_gas_price 
        }

        return self._put_request(url, body)

    def _get_request(self, path):
        token = self.token_provider.sign_jwt(path)
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(self.base_url + path, headers=headers)
        if response.status_code >= 300:
            raise FireblocksApiException("Got an error from fireblocks server: " + response.text)
        else:
            return response.json()

    def _delete_request(self, path):
        token = self.token_provider.sign_jwt(path)
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}"
        }

        response = requests.delete(self.base_url + path, headers=headers)
        if response.status_code >= 300:
            raise FireblocksApiException("Got an error from fireblocks server: " + response.text)
        else:
            return response.json()

    def _post_request(self, path, body={}):
        token = self.token_provider.sign_jwt(path, body)
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}"
        }

        response = requests.post(self.base_url + path, headers=headers, json=body)
        if response.status_code >= 300:
            raise FireblocksApiException("Got an error from fireblocks server: " + response.text)
        else:
            return response.json()

    def _put_request(self, path, body={}):
        token = self.token_provider.sign_jwt(path, body)
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.put(self.base_url + path, headers=headers, data=json.dumps(body))
        if response.status_code >= 300:
            raise FireblocksApiException("Got an error from fireblocks server: " + response.text)
        else:
            return response.json()






