from __future__ import annotations

from typing import Dict, Union

from fireblocks_sdk.entities.network_id import NetworkId
from fireblocks_sdk.entities.routing_policy import RoutingPolicy


class NetworkConnectionResponse:
    def __init__(self, id: str, status: str, legacy_address: NetworkId,
                 enterprise_address: NetworkId, routing_policy: Union[RoutingPolicy, None]) -> None:
        self.routing_policy = routing_policy
        self.id = id
        self.status = status
        self.legacy_address = legacy_address
        self.enterprise_address = enterprise_address

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> NetworkConnectionResponse:
        return cls(
            data.get('id'),
            data.get('status'),
            NetworkId.deserialize(data.get('remoteNetworkId')),
            NetworkId.deserialize(data.get('localNetworkId')),
            RoutingPolicy.deserialize(data.get('routingPolicy', {}))
        )
