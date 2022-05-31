from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class GasStationInfoConfiguration(Deserializable):

    def __init__(self, gas_threshold: str, gas_cap: str, max_gas_price: str) -> None:
        super().__init__()
        self.gas_threshold = gas_threshold
        self.gas_cap = gas_cap
        self.max_gas_price = max_gas_price

    @classmethod
    def deserialize(cls, data: Dict[str]) -> GasStationInfoConfiguration:
        return cls(
            data.get('gasThreshold'),
            data.get('gasCap'),
            data.get('maxGasPrice'),
        )


class GasStationInfo(Deserializable):

    def __init__(self, balance: Dict[str, str], configuration: GasStationInfoConfiguration) -> None:
        super().__init__()
        self.balance = balance
        self.configuration = configuration

    @classmethod
    def deserialize(cls, data: Dict[str]) -> GasStationInfo:
        return cls(
            data.get('balance'),
            GasStationInfoConfiguration.deserialize(data.get('configuration'))
        )
