from typing import Union

from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.entities.op_success_response import OperationSuccessResponse
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.wallets.external_wallet_asset import ExternalWalletAsset
from fireblocks_sdk.services.wallets.wallet_container_response import WalletContainerResponse


class ContractsService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    @response_deserializer(ExternalWalletAsset)
    def get_contract_wallets(self) -> ExternalWalletAsset:
        """Gets all contract wallets for your tenant      
        """
        return self.connector.get(f"/v1/contracts").content

    @response_deserializer(ExternalWalletAsset)
    def get_contract_wallet(self, wallet_id) -> ExternalWalletAsset:
        """Gets a single contract wallet

        Args:
        wallet_id (str): The contract wallet ID
        """
        return self.connector.get(f"/v1/contracts/{wallet_id}").content

    @response_deserializer(ExternalWalletAsset)
    def get_contract_wallet_asset(self, wallet_id, asset_id) -> ExternalWalletAsset:
        """Gets a single contract wallet asset

        Args:
        wallet_id (str): The contract wallet ID
        asset_id (str): The asset ID
        """
        return self.connector.get(f"/v1/contracts/{wallet_id}/{asset_id}").content

    @response_deserializer(WalletContainerResponse[ExternalWalletAsset])
    def create_contract_wallet(self, name, idempotency_key=None) -> WalletContainerResponse[ExternalWalletAsset]:
        """Creates a new contract wallet

        Args:
        name (str): A name for the new contract wallet
        """
        return self.connector.post("/v1/contracts", {"name": name}, idempotency_key).content

    @response_deserializer(ExternalWalletAsset)
    def create_contract_wallet_asset(self, wallet_id: str, asset_id: str, address: str, tag: Union[str, None] = None,
                                     idempotency_key: Union[str, None] = None) -> ExternalWalletAsset:
        """Creates a new contract wallet asset

        Args:
        wallet_id (str): The wallet id
        assetId (str): The asset to add
        address (str): The wallet address
        tag (str): (for ripple only) The ripple account tag
        """
        return self.connector.post(f"/v1/contracts/{wallet_id}/{asset_id}", {"address": address, "tag": tag},
                                   idempotency_key).content

    @response_deserializer(OperationSuccessResponse)
    def delete_contract_wallet(self, wallet_id: str) -> OperationSuccessResponse:
        """Deletes a single contract wallet

        Args:
            wallet_id (string): The contract wallet ID
        """
        return self.connector.delete(f"/v1/contracts/{wallet_id}").content

    @response_deserializer(OperationSuccessResponse)
    def delete_contract_wallet_asset(self, wallet_id: str, asset_id: str) -> OperationSuccessResponse:
        """Deletes a single contract wallet

        Args:
            wallet_id (string): The contract wallet ID
            asset_id (string): The asset ID
        """

        return self.connector.delete(f"/v1/contracts/{wallet_id}/{asset_id}").content
