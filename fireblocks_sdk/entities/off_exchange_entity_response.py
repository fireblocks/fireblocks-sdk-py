from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable, T


class ExchangeBalance(Deserializable):
    def __init__(self, total: str, locked: str, pending: str, frozen: str) -> None:
        super().__init__()
        self.total = total
        self.locked = locked
        self.pending = pending
        self.frozen = frozen

    @classmethod
    def deserialize(cls: T, data: Dict[str]) -> ExchangeBalance:
        return ExchangeBalance(data.get('total'), data.get('locked'), data.get('pending'), data.get('frozen'))


class OffExchangeEntityResponse(Deserializable):
    def __init__(self, id: str, vault_account_id: str, third_party_account_id: str) -> None:
        self.id = id
        self.vault_account_id = vault_account_id
        self.third_party_account_id = third_party_account_id
        self.balance: Dict[str, ExchangeBalance] = {}

    def set_balance(self, asset_id: str, balance: ExchangeBalance):
        self.balance[asset_id] = balance

    @classmethod
    def deserialize(cls, data: Dict[str]) -> OffExchangeEntityResponse:
        response = cls(data.get('id'), data.get('vaultAccountId'), data.get('thirdPartyAccountId'))
        for k, v in data.get('balance', {}).items():
            response.set_balance(k, ExchangeBalance.deserialize(v))

        return response
