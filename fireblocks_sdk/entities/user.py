from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class User(Deserializable):

    def __init__(self, id: str, first_name: str, last_name: str, email: str, enabled: bool, role: str) -> None:
        super().__init__()
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.enabled = enabled
        self.role = role

    @classmethod
    def deserialize(cls, data: Dict[str]) -> User:
        return User(data.get('id'), data.get('firstName'), data.get('lastName'), data.get('email'), data.get('enabled'),
                    data.get('role'))
