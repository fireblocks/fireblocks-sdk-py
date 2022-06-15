from __future__ import annotations

from typing import Union, Dict

from fireblocks_sdk.entities.routing_dest import RoutingDest


class RoutingPolicy:
    def __init__(self, crypto: Union[RoutingDest, None], sen: Union[RoutingDest, None],
                 signet: Union[RoutingDest, None], sen_test: Union[RoutingDest, None],
                 signet_test: Union[RoutingDest, None]) -> None:
        self.crypto = crypto
        self.sen = sen
        self.signet = signet
        self.sen_test = sen_test
        self.signet_test = signet_test

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> RoutingPolicy:
        return RoutingPolicy(
            data.get('crypto'),
            data.get('sen'),
            data.get('signet'),
            data.get('sen_test'),
            data.get('signet_test'),
        )
