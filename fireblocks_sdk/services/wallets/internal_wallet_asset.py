from __future__ import annotations

from typing import Dict

from fireblocks_sdk.services.wallets.external_wallet_asset import ExternalWalletAsset


class InternalWalletAsset(ExternalWalletAsset):
    def __init__(self, id: str, status: str, address: str, tag: str, activation_time: str, balance: str) -> None:
        super().__init__(id, status, address, tag, activation_time)
        self.balance = balance

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> InternalWalletAsset:
        wallet = super().deserialize(data)
        return InternalWalletAsset(
            wallet.id, wallet.status, wallet.address, wallet.tag, wallet.activation_time, data.get('balance')
        )
