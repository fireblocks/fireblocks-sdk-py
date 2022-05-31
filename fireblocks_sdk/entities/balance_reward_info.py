from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class BalanceRewardInfo(Deserializable):

    def __init__(self, pending_rewards: str) -> None:
        super().__init__()
        self.pending_rewards = pending_rewards

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> BalanceRewardInfo:
        return cls(data.get('pendingRewards'))
