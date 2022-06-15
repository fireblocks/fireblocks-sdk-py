from __future__ import annotations

from typing import Dict


class RoutingDest:
    def __init__(self, scheme: str, dst_type: str, dst_id: str) -> None:
        self.scheme = scheme
        self.dst_type = dst_type
        self.dst_id = dst_id

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> RoutingDest:
        return RoutingDest(
            data.get('scheme'),
            data.get('dstType'),
            data.get('dstId')
        )
