from __future__ import annotations

from typing import Generic, TypeVar, Dict, Union, List

from fireblocks_sdk.entities.deserializable import Deserializable

T = TypeVar('T', bound=Deserializable)


class WalletContainerResponse(Generic[T]):

    def __init__(self, id: str, name: str, assets: List[T], customer_ref_id: Union[str, None]) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.assets = assets
        self.customer_ref_id = customer_ref_id

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> WalletContainerResponse[T]:
        return cls(
            data.get('id'),
            data.get('name'),
            [T.deserialize(asset) for asset in data.get('assets')],
            data.get('customerRefId'),
        )
