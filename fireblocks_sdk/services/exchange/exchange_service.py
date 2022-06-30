from typing import Union

from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.entities.op_success_response import OperationSuccessResponse
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.exchange.convert_exchange_asset_response import ConvertExchangeAssetResponse
from fireblocks_sdk.services.exchange.exchange_response import ExchangeResponse


class ExchangeService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    @response_deserializer(ExchangeResponse)
    def get_exchange_accounts(self):
        """Gets all exchange accounts for your tenant"""

        response = self.connector.get("/v1/exchange_accounts")
        return [ExchangeResponse.deserialize(exchange) for exchange in response.content]

    @response_deserializer(ExchangeResponse)
    def get_exchange_account_by_id(self, exchange_account_id: str) -> ExchangeResponse:
        """Gets an exchange account for your tenant
        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
        """

        return self.connector.get(f"/v1/exchange_accounts/{exchange_account_id}").content

    @response_deserializer(ExchangeResponse)
    def get_exchange_asset(self, exchange_account_id: str, asset_id: str) -> ExchangeResponse:
        """Get a specific asset from an exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            asset_id (string): The asset to transfer
        """

        return self.connector.get(f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}").content

    @response_deserializer(ConvertExchangeAssetResponse)
    def convert_exchange_asset(self, exchange_account_id: str, source_asset_id: str, destination_asset_id: str, amount: float) -> ExchangeResponse:
        body = {
            "srcAsset": source_asset_id,
            "destAsset": destination_asset_id,
            "amount": amount

        }

        return self.connector.post(f"/v1/exchange_accounts/{exchange_account_id}/convert", body).content

    @response_deserializer(OperationSuccessResponse)
    def transfer_to_subaccount(self, exchange_account_id: str, sub_account_id: str, asset_id: str, amount: float,
                               idempotency_key: Union[str, None] = None) -> OperationSuccessResponse:
        """Transfer to a subaccount from a main exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            sub_account_id (string): The ID of the subaccount in the exchange
            asset_id (string): The asset to transfer
            amount (float): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {
            "subaccountId": sub_account_id,
            "amount": amount
        }

        return self.connector.post(f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}/transfer_to_subaccount",
                                   body, idempotency_key).content

    @response_deserializer(OperationSuccessResponse)
    def transfer_from_subaccount(self, exchange_account_id: str, sub_account_id: str, asset_id: str, amount: float,
                                 idempotency_key: Union[str, None] = None) -> OperationSuccessResponse:
        """Transfer from a subaccount to a main exchange account

        Args:
            exchange_account_id (string): The exchange ID in Fireblocks
            sub_account_id (string): The ID of the subaccount in the exchange
            asset_id (string): The asset to transfer
            amount (float): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {
            "subaccountId": sub_account_id,
            "amount": amount
        }

        return self.connector.post(
            f"/v1/exchange_accounts/{exchange_account_id}/{asset_id}/transfer_from_subaccount",
            body, idempotency_key).content
