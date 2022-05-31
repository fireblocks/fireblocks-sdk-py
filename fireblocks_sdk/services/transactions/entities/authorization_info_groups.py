from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class AuthorizationInfoGroups(Deserializable):

    def __init__(self, users: Dict[str, str], th: int) -> None:
        super().__init__()
        self.users = users
        self.th = th

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> AuthorizationInfoGroups:
        return cls(
            data.get('users'),
            data.get('th')
        )
