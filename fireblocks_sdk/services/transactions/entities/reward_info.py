from __future__ import annotations

from typing import Dict

from fireblocks_sdk.entities.deserializable import Deserializable


class RewardInfo(Deserializable):

    def __init__(self, src_rewards: str, dest_rewards: str) -> None:
        super().__init__()
        self.src_rewards = src_rewards
        self.dest_rewards = dest_rewards

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> RewardInfo:
        return cls(
            data.get('srcRewards'),
            data.get('destRewards')
        )
