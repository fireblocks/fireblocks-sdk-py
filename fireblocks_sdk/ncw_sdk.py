from .sdk import FireblocksSDK
import urllib

class FireblocksNCW:
    def __init__(self, sdk: FireblocksSDK):
        self.sdk = sdk
        self._wallet_url = "/v1/wallets"

    def create_wallet(self):
        url = "/v1/wallets"
        return self.sdk._post_request(url)

    def get_wallets(self):
        return self.sdk._get_request(self._wallet_url)

    def get_wallet(self, wallet_id: str):
        url = f"{self._wallet_url}/{wallet_id}"
        return self.sdk._get_request(url)

    def enable_wallet(self, wallet_id: str, enabled: bool):
        url = f"{self._wallet_url}/{wallet_id}/enable"
        body = {"enabled": enabled}
        return self.sdk._put_request(url, body)

    def create_wallet_account(self, wallet_id: str):
        url = f"{self._wallet_url}/{wallet_id}/accounts"
        return self.sdk._post_request(url)

    def get_wallet_accounts(
        self,
        wallet_id: str,
        page_cursor: str = None,
        page_size: int = None,
        sort: str = None,
        order: str = None,
        enabled: bool = None,
    ):
        url = f"{self._wallet_url}/{wallet_id}/accounts"
        query_params = {}

        if page_cursor:
            query_params["pageCursor"] = page_cursor

        if page_size:
            query_params["pageSize"] = page_size

        if sort:
            query_params["sort"] = sort

        if order:
            query_params["order"] = order

        if enabled:
            query_params["enabled"] = enabled

        return self.sdk._get_request(url, query_params=query_params)

    def get_wallet_account(self, wallet_id: str, account_id: str):
        url = f"{self._wallet_url}/{wallet_id}/accounts/{account_id}"
        return self.sdk._get_request(url)

    def get_wallet_assets(
        self,
        wallet_id: str,
        account_id: str,
        page_cursor: str = None,
        page_size: int = None,
        sort: str = None,
        order: str = None,
        enabled: bool = None,
    ):
        url = f"{self._wallet_url}/{wallet_id}/accounts/{account_id}/assets"
        query_params = {}

        if page_cursor:
            query_params["pageCursor"] = page_cursor

        if page_size:
            query_params["pageSize"] = page_size

        if sort:
            query_params["sort"] = sort

        if order:
            query_params["order"] = order

        if enabled:
            query_params["enabled"] = enabled

        return self.sdk._get_request(url, query_params=query_params)

    def get_wallet_asset(self, wallet_id: str, account_id: str, asset_id: str):
        url = f"{self._wallet_url}/{wallet_id}/accounts/{account_id}/assets/{asset_id}"
        return self.sdk._get_request(url)

    def activate_wallet_asset(self, wallet_id: str, account_id: str, asset_id: str):
        url = f"{self._wallet_url}/{wallet_id}/accounts/{account_id}/assets/{asset_id}"
        return self.sdk._post_request(url)

    def refresh_wallet_asset_balance(
        self, wallet_id: str, account_id: str, asset_id: str
    ):
        url = f"{self._wallet_url}/{wallet_id}/accounts/{account_id}/assets/{asset_id}/balance"
        return self.sdk._put_request(url)

    def get_wallet_asset_balance(
        self, wallet_id: str, account_id: str, asset_id: str
    ):
        url = f"{self._wallet_url}/{wallet_id}/accounts/{account_id}/assets/{asset_id}/balance"
        return self.sdk._get_request(url)

    def get_wallet_asset_addresses(
        self,
        wallet_id: str,
        account_id: str,
        asset_id: str,
        page_cursor: str = None,
        page_size: int = None,
        sort: str = None,
        order: str = None,
        enabled: bool = None,
    ):
        url = f"{self._wallet_url}/{wallet_id}/accounts/{account_id}/assets/{asset_id}/addresses"
        query_params = {}

        if page_cursor:
            query_params["pageCursor"] = page_cursor

        if page_size:
            query_params["pageSize"] = page_size

        if sort:
            query_params["sort"] = sort

        if order:
            query_params["order"] = order

        if enabled:
            query_params["enabled"] = enabled

        return self.sdk._get_request(url, query_params=query_params)

    def get_devices(self, wallet_id: str):
        url = f"{self._wallet_url}/{wallet_id}/devices"
        return self.sdk._get_request(url)

    def enable_device(self, wallet_id: str, device_id: str, enabled: bool):
        url = f"{self._wallet_url}/{wallet_id}/devices/{device_id}"
        body = {"enabled": enabled}

        return self.sdk._put_request(url, body)

    def invoke_wallet_rpc(self, wallet_id: str, device_id: str, payload: str):
        """
        payload: stringified JSON, message originated in the NCW SDK
        """
        url = f"{self._wallet_url}/{wallet_id}/devices/{device_id}/rpc"
        body = {"payload": payload}

        return self.sdk._post_request(url, body)
    
    def get_public_key_info(self, wallet_id: str, algorithm: str, derivation_path: str, compressed=None):
        """Get the public key information

        Args:
            wallet_id (str)
            algorithm (str)
            derivation_path (str)
            compressed (boolean, optional)
        """

        url = f"/v1/ncw/wallet/${wallet_id}/public_key_info"
        if algorithm:
            url += f"?algorithm={algorithm}"
        if derivation_path:
            url += f"&derivationPath={urllib.parse.quote(derivation_path)}"
        if compressed:
            url += f"&compressed={compressed}"
        return self.sdk._get_request(url, None, None, wallet_id)

    def get_public_key_info_by_account_asset(
            self, wallet_id: str, asset_id: str, account_id: int, change: int, address_index: int, compressed=None
    ):
        """Get the public key information for an NCW account

        Args:
            wallet_id (str)
            asset_id (str)
            account_id (number)
            change (number)
            address_index (number)
            compressed (boolean, optional)
        """

        url = f"/v1/ncw/wallet/${wallet_id}/accounts/{account_id}/{asset_id}/{change}/{address_index}/public_key_info"
        if compressed:
            url += f"?compressed={compressed}"

        return self.sdk._get_request(url, None, None, wallet_id)

