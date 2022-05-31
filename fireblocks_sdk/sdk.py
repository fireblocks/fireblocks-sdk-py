from typing import List

from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.entities.asset_type import AssetType
from fireblocks_sdk.entities.network_connection_response import NetworkConnectionResponse
from fireblocks_sdk.services.transfer_tickets.transfer_tickets_service import TransferTicketsService
from fireblocks_sdk.services.vaults.vaults_service import VaultsService
from fireblocks_sdk.services.wallets.wallets_service import WalletsService
from fireblocks_sdk.services.web_hooks.web_hooks_service import WebHooksService
from .common.wrappers import response_deserializer
from .sdk_token_provider import SdkTokenProvider
from .services.contracts.contracts_service import ContractsService
from .services.exchange.exchange_service import ExchangeService
from .services.gas_station.gas_station_service import GasStationService
from .services.transactions.transactions_service import TransactionsService


class FireblocksSDK:

    def __init__(self, private_key, api_key, api_base_url="https://api.fireblocks.io", timeout=None):
        """Creates a new Fireblocks API Client.

        Args:
            private_key (str): A string representation of your private key (in PEM format)
            api_key (str): Your api key. This is a uuid you received from Fireblocks
            base_url (str): The fireblocks server URL. Leave empty to use the default server
            timeout (number): Timeout for http requests in seconds
        """
        self.private_key = private_key

        self.connector = RestConnector(SdkTokenProvider(private_key, api_key), api_base_url, api_key, timeout)
        self.vault = VaultsService(self.connector)
        self.exchange = ExchangeService(self.connector)
        self.contracts = ContractsService(self.connector)
        self.wallets = WalletsService(self.connector)
        self.gas_station = GasStationService(self.connector)
        self.transfer_tickets = TransferTicketsService(self.connector)
        self.transactions = TransactionsService(self.connector)
        self.web_hooks = WebHooksService(self.connector)

    def get_supported_assets(self) -> List[AssetType]:
        """Gets all assets that are currently supported by Fireblocks"""

        response = self.connector.get("/v1/supported_assets")
        return [AssetType.deserialize(asset) for asset in response.content]

    @response_deserializer(NetworkConnectionResponse)
    def get_network_connections(self) -> List[NetworkConnectionResponse]:
        """Gets all network connections for your tenant"""

        return self.connector.get("/v1/network_connections").content

    @response_deserializer(NetworkConnectionResponse)
    def get_network_connection_by_id(self, connection_id) -> NetworkConnectionResponse:
        """Gets a single network connection by id
        Args:
            connection_id (string): The ID of the network connection
        """

        return self.connector.get(f"/v1/network_connections/{connection_id}").content

    def get_fee_for_asset(self, asset_id):
        """Gets the estimated fees for an asset

        Args:
            asset_id (str): The asset symbol (e.g BTC, ETH)
        """

        return self.connector.get(f"/v1/estimate_network_fee?assetId={asset_id}")

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

        return self.connector.post(f"/v1/txHash/{txhash}/set_confirmation_threshold", body, idempotency_key)

    def get_users(self):
        """Gets all users of your tenant"""

        url = "/v1/users"

        return self.connector.get(url)

    def get_off_exchanges(self):
        """
        Get your connected off exchanges virtual accounts
        """
        url = f"/v1/off_exchange_accounts"

        return self.connector.get(url)

    def get_off_exchange_by_id(self, off_exchange_id):
        """
        Get your connected off exchange by it's ID
        :param off_exchange_id: ID of the off exchange virtual account
        :return: off exchange entity
        """

        url = f"/v1/off_exchange_accounts/{off_exchange_id}"

        return self.connector.get(url)

    def settle_off_exchange_by_id(self, off_exchange_id, idempotency_key=None):
        """
        Create a settle request to your off exchange by it's ID
        :param off_exchange_id: ID of the off exchange virtual account
        :param idempotency_key
        """

        url = f"/v1/off_exchanges/{off_exchange_id}/settle"

        return self.connector.post(url, {}, idempotency_key)
