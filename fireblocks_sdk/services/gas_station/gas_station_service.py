from typing import Union

from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.entities.op_success_response import OperationSuccessResponse
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.gas_station.gas_station_info import GasStationInfo


class GasStationService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    @response_deserializer(GasStationInfo)
    def get_gas_station_info(self, asset_id: Union[str, None] = None) -> GasStationInfo:
        """Get configuration and status of the Gas Station account"

        Args:
            asset_id (string, optional)
        """

        url = f"/v1/gas_station"

        if asset_id:
            url = url + f"/{asset_id}"

        return self.connector.get(url).content

    @response_deserializer(OperationSuccessResponse)
    def set_gas_station_configuration(self, gas_threshold: str, gas_cap: str, max_gas_price: Union[str, None] = None,
                                      asset_id: Union[str, None] = None) -> OperationSuccessResponse:
        """Set configuration of the Gas Station account

        Args:
            gas_threshold (str)
            gas_cap (str)
            max_gas_price (str, optional)
            asset_id (str, optional)
        """

        url = f"/v1/gas_station/configuration"

        if asset_id:
            url = url + f"/{asset_id}"

        body = {
            "gasThreshold": gas_threshold,
            "gasCap": gas_cap,
            "maxGasPrice": max_gas_price
        }

        return self.connector.put(url, body).content
