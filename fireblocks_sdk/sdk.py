import requests
import urllib

from .sdk_token_provider import SdkTokenProvider
from .api_types import FireblocksApiException, TRANSACTION_TYPES, TRANSACTION_STATUS_TYPES, PEER_TYPES, TransferPeerPath, TRANSACTION_TRANSFER

class FireblocksSDK(object):

    def __init__(self, private_key, api_key, api_base_url="https://api.fireblocks.io"):
        """Creates a new Fireblocks API Client.

        Args:
            private_key (str): A string representation of your private key
            api_key (str): Your api key. This is a uuid you received from Fireblocks
            api_key (str): The fireblocks server URL. Leave empty to use the default server            
        """        
        self.private_key = private_key
        self.api_key = api_key
        self.base_url = api_base_url
        self.token_provider = SdkTokenProvider(private_key, api_key)

    def get_vault_accounts(self):
        """Gets all vault accounts for your tenant"""

        return self._get_request("/v1/vault/accounts")

    def get_vault_account(self, vault_account_id):
        """Gets a single vault account        
        Args:
            vault_account_id (string): The id of the requested account
        """        

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}")

    def get_vault_account_asset(self, vault_account_id, asset_id):
        """Gets a single vault account asset        
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The id of the requested asset
        """        

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}")

    def get_deposit_addresses(self, vault_account_id, asset_id):
        """Gets deposit addresses for an asset in a vault account
        Args:
            vault_account_id (string): The id of the requested account
            asset_id (string): The id of the requested asset
        """        

        return self._get_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}/addresses")

    def get_exchange_accounts(self):
        """Gets all exchange accounts for your tenant"""

        return self._get_request("/v1/exchange_accounts")

    def get_transactions(self, before=0, after=0, status=None):
        """Gets a list of transactions matching the given filter

        Args:
            before (int, optional): Only gets transactions created before given timestamp (in seconds)
            after (int, optional): Only gets transactions created after given timestamp (in seconds)
            print_cols (str, optional): Only gets transactions with the specified status
        """        

        path = "/v1/transactions"
        
        params = {}

        if status and status not in TRANSACTION_STATUS_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + tx_type)

        if before:
            params['before'] = before
        if after:
            params['after'] = after
        if status:
            params['status'] = status

        if params:
            path = path + "?" + urllib.parse.urlencode(params)
        
        return self._get_request(path)

    def get_internal_wallets(self):
        """Gets all internal wallets for your tenant"""        

        return self._get_request("/v1/internal_wallets")

    def get_external_wallets(self):
        """Gets all external wallets for your tenant"""        

        return self._get_request("/v1/external_wallets")

    def get_transaction_by_id(self, txid):
        """Gets detailed information for a single transaction

        Args:
            txid (str): The transaction id to query
        """        

        return self._get_request(f"/v1/transactions/{txid}")

    def cancel_transaction_by_id(self, txid):
        """Cancels the selected transaction

        Args:
            txid (str): The transaction id to cancel
        """        

        return self._post_request(f"/v1/transactions/{txid}/cancel")        

    def create_vault_account(self, name):
        """Creates a new vault account.

        Args:
            name (str): A name for the new vault account
        """        

        return self._post_request("/v1/vault/accounts", {"name": name})

    def create_vault_asset(self, vault_account_id, asset_id):
        """Creates a new asset within an existing vault account

        Args:
            vault_account_id (str): The vault account Id
            asset_id (str): The asset to add
        """        

        return self._post_request(f"/v1/vault/accounts/{vault_account_id}/{asset_id}")

    def create_external_wallet(self, name):
        """Creates a new external wallet

        Args:
            name (str): A name for the new external wallet
        """        

        return self._post_request("/v1/external_wallets", {"name": name})

    def create_internal_wallet(self, name):
        """Creates a new internal wallet

        Args:
            name (str): A name for the new internal wallet
        """        

        return self._post_request("/v1/internal_wallets", {"name": name})

    def create_external_wallet_asset(self, wallet_id, asset_id, address, tag=None):
        """Creates a new asset within an exiting external wallet

        Args:
            wallet_id (str): The wallet id
            asset_id (str): The asset to add
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
            asset_id (str): The asset to add
            address (str): The wallet address
            tag (str, optional): (for ripple only) The ripple account tag 
        """        

        body = {"address": address}
        if tag:
            body["tag"] = tag
        
        return self._post_request(
            f"/v1/internal_wallets/{wallet_id}/{asset_id}", body
            )            


    def create_transaction(self, asset_id, amount, source, destination=None , fee=-1, wait_for_status=False, tx_type=TRANSACTION_TRANSFER):
        """Creates a new transaction

        Args:
            asset_id (str): The asset symbol
            source (TransferPeerType): The transfer source
            destination (TransferPeerType, optional): The transfer destination
            amount (int): The amount
            fee (int, optional): The fee
            wait_for_status (bool, optional): If true, waits for transaction status. Default is false.
            tx_type (str, optional): Transaction type: either TRANSFER, MINT or BURN. Default is TRANSFER.                
        """        

        if tx_type not in TRANSACTION_TYPES:
            raise FireblocksApiException("Got invalid transaction type: " + tx_type)

        body = {
            "assetId": asset_id,
            "amount": amount,            
            "source": source.__dict__,
            "fee": fee,
            "waitForStatus": wait_for_status,
            "operation": tx_type
        }

        if destination:
            body["destination"] = destination.__dict__

        return self._post_request("/v1/transactions", body)


    def _get_request(self, path):
        token = self.token_provider.sign_jwt(path)
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}"           
        }

        response = requests.get(self.base_url + path, headers=headers)
        if response.status_code != 200:
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
        if response.status_code != 200:
            raise FireblocksApiException("Got an error from fireblocks server: " + response.text)
        else:
            return response.json()



    





