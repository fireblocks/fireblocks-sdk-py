from typing import Union

from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.fee_payer.fee_payer_configuration import FeePayerConfiguration


class FeePayerService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    @response_deserializer(FeePayerConfiguration)
    def set_fee_payer_configuration(self, base_asset: str, fee_payer_account_id: str,
                                    idempotency_key: Union[str, None] = None) -> FeePayerConfiguration:
        """
        Setting fee payer configuration for base asset
        :param base_asset: ID of the base asset you want to configure fee payer for (for example: SOL)
        :param fee_payer_account_id: ID of the vault account you want your fee to be paid from
        :param idempotency_key
        """

        url = f"/v1/fee_payer/{base_asset}"

        body = {
            "feePayerAccountId": fee_payer_account_id
        }

        return self.connector.post(url, body, idempotency_key).content

    @response_deserializer(FeePayerConfiguration)
    def get_fee_payer_configuration(self, base_asset: str) -> FeePayerConfiguration:
        """
        Get fee payer configuration for base asset
        :param base_asset: ID of the base asset
        :return: the fee payer configuration
        """

        url = f"/v1/fee_payer/{base_asset}"

        return self.connector.get(url).content

    def remove_fee_payer_configuration(self, base_asset: str):
        """
        Delete fee payer configuration for base asset
        :param base_asset: ID of the base asset
        """
        url = f"/v1/fee_payer/{base_asset}"

        return self.connector.delete(url)
