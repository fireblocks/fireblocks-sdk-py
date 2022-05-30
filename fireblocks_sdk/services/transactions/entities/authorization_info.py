from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable
from fireblocks_sdk.services.transactions.entities.authorization_info_groups import AuthorizationInfoGroups


class AuthorizationInfo(Deserializable):

    def __init__(self, allow_operator_as_authorizer: bool, logic: str, groups: AuthorizationInfoGroups) -> None:
        super().__init__()
        self.allow_operator_as_authorizer = allow_operator_as_authorizer
        self.logic = logic
        self.groups = groups

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> AuthorizationInfo:
        return cls(
            data.get('allowOperatorAsAuthorizer'),
            data.get('logic'),
            AuthorizationInfoGroups.deserialize(data.get('groups', {}))
        )
