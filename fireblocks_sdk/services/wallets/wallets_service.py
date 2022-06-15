from typing import Union, List

from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.wallets.external_wallet_asset import ExternalWalletAsset
from fireblocks_sdk.services.wallets.internal_wallet_asset import InternalWalletAsset
from fireblocks_sdk.services.wallets.wallet_container_response import WalletContainerResponse


class WalletsService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    def delete_internal_wallet(self, wallet_id: str):
        """Deletes a single internal wallet

        Args:
            wallet_id (string): The internal wallet ID
        """

        return self.connector.delete(f"/v1/internal_wallets/{wallet_id}")

    def delete_external_wallet(self, wallet_id: str):
        """Deletes a single external wallet

        Args:
            wallet_id (string): The external wallet ID
        """

        return self.connector.delete(f"/v1/external_wallets/{wallet_id}")

    def get_internal_wallets(self):
        """Gets all internal wallets for your tenant"""

        return self.connector.get("/v1/internal_wallets")

    def delete_internal_wallet_asset(self, wallet_id: str, asset_id: str):
        """Deletes a single asset from an internal wallet

        Args:
            wallet_id (string): The internal wallet ID
            asset_id (string): The asset ID
        """

        return self.connector.delete(f"/v1/internal_wallets/{wallet_id}/{asset_id}")

    def delete_external_wallet_asset(self, wallet_id: str, asset_id: str):
        """Deletes a single asset from an external wallet

        Args:
            wallet_id (string): The external wallet ID
            asset_id (string): The asset ID
        """

        return self.connector.delete(f"/v1/external_wallets/{wallet_id}/{asset_id}")

    def set_customer_ref_id_for_internal_wallet(self, wallet_id: str, customer_ref_id: Union[str, None] = None,
                                                idempotency_key: Union[str, None] = None):
        """Sets an AML/KYT customer reference ID for the specific internal wallet

        Args:
            wallet_id (string): The external wallet ID
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self.connector.post(f"/v1/internal_wallets/{wallet_id}/set_customer_ref_id",
                                   {"customerRefId": customer_ref_id or ''}, idempotency_key)

    def set_customer_ref_id_for_external_wallet(self, wallet_id: str, customer_ref_id: Union[str, None] = None,
                                                idempotency_key: Union[str, None] = None):
        """Sets an AML/KYT customer reference ID for the specific external wallet

        Args:
            wallet_id (string): The external wallet ID
            customer_ref_id (str): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self.connector.post(f"/v1/external_wallets/{wallet_id}/set_customer_ref_id",
                                   {"customerRefId": customer_ref_id or ''}, idempotency_key)

    @response_deserializer(WalletContainerResponse[InternalWalletAsset])
    def get_internal_wallet(self, wallet_id: str) -> WalletContainerResponse[InternalWalletAsset]:
        """Gets an internal wallet from your tenant
        Args:
            wallet_id (str): The wallet id to query
        """

        return self.connector.get(f"/v1/internal_wallets/{wallet_id}").content

    @response_deserializer(InternalWalletAsset)
    def get_internal_wallet_asset(self, wallet_id: str, asset_id: str) -> InternalWalletAsset:
        """Gets an asset from an internal wallet from your tenant
        Args:
            wallet_id (str): The wallet id to query
            asset_id (str): The asset id to query
        """
        return self.connector.get(f"/v1/internal_wallets/{wallet_id}/{asset_id}").content

    @response_deserializer(List[WalletContainerResponse[ExternalWalletAsset]])
    def get_external_wallets(self):
        """Gets all external wallets for your tenant"""

        return self.connector.get("/v1/external_wallets").content

    @response_deserializer(WalletContainerResponse[ExternalWalletAsset])
    def get_external_wallet(self, wallet_id: str) -> WalletContainerResponse[ExternalWalletAsset]:
        """Gets an external wallet from your tenant
        Args:
            wallet_id (str): The wallet id to query
        """

        return self.connector.get(f"/v1/external_wallets/{wallet_id}").content

    @response_deserializer(ExternalWalletAsset)
    def get_external_wallet_asset(self, wallet_id: str, asset_id: str) -> ExternalWalletAsset:
        """Gets an asset from an external wallet from your tenant
        Args:
            wallet_id (str): The wallet id to query
            asset_id (str): The asset id to query
        """
        return self.connector.get(f"/v1/external_wallets/{wallet_id}/{asset_id}").content

    @response_deserializer(ExternalWalletAsset)
    def create_external_wallet_asset(self, wallet_id: str, asset_id: str, address: str, tag: Union[str, None] = None,
                                     idempotency_key: Union[str, None] = None) -> ExternalWalletAsset:
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

        return self.connector.post(
            f"/v1/external_wallets/{wallet_id}/{asset_id}", body, idempotency_key
        ).content

    @response_deserializer(InternalWalletAsset)
    def create_internal_wallet_asset(self, wallet_id: str, asset_id: str, address: str, tag: Union[str, None] = None,
                                     idempotency_key: Union[str, None] = None) -> InternalWalletAsset:
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

        return self.connector.post(
            f"/v1/internal_wallets/{wallet_id}/{asset_id}", body, idempotency_key
        ).content

    @response_deserializer(WalletContainerResponse[ExternalWalletAsset])
    def create_external_wallet(self, name: str, customer_ref_id: Union[str, None] = None,
                               idempotency_key: Union[str, None] = None) -> (
    WalletContainerResponse[ExternalWalletAsset]):
        """Creates a new external wallet

        Args:
            name (str): A name for the new external wallet
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self.connector.post("/v1/external_wallets", {"name": name, "customerRefId": customer_ref_id or ''},
                                   idempotency_key).content

    @response_deserializer(WalletContainerResponse[InternalWalletAsset])
    def create_internal_wallet(self, name: str, customer_ref_id: Union[str, None] = None,
                               idempotency_key: Union[str, None] = None) -> WalletContainerResponse[
        InternalWalletAsset]:
        """Creates a new internal wallet

        Args:
            name (str): A name for the new internal wallet
            customer_ref_id (str, optional): The ID for AML providers to associate the owner of funds with transactions
            idempotency_key (str, optional)
        """

        return self.connector.post("/v1/internal_wallets", {"name": name, "customerRefId": customer_ref_id or ''},
                                   idempotency_key).content
