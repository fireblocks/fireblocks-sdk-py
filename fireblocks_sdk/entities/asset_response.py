from __future__ import annotations

from typing import Dict, Union

from fireblocks_sdk.entities.allocated_balances import AllocatedBalances
from fireblocks_sdk.entities.balance_reward_info import BalanceRewardInfo
from fireblocks_sdk.entities.deserializable import Deserializable


class AssetResponse(Deserializable):
    def __init__(self, id: str, total: str, balance: Union[str, None], locked_amount: Union[str, None], available: str,
                 pending: str,
                 self_staked_cpu: Union[str, None], self_staked_network: Union[str, None],
                 pending_refund_cpu: Union[str, None], pending_refund_network: Union[str, None],
                 total_staked_cpu: Union[str, None], total_staked_network: Union[str, None],
                 reward_info: Union[BalanceRewardInfo, None], block_height: Union[str, None],
                 block_hash: Union[str, None],
                 allocated_balances: Union[AllocatedBalances, None]) -> None:
        self.id = id
        self.total = total
        self.balance = balance
        self.locked_amount = locked_amount
        self.available = available
        self.pending = pending
        self.self_staked_cpu = self_staked_cpu
        self.self_staked_network = self_staked_network
        self.pending_refund_cpu = pending_refund_cpu
        self.pending_refund_network = pending_refund_network
        self.total_staked_cpu = total_staked_cpu
        self.total_staked_network = total_staked_network
        self.reward_info = reward_info
        self.block_height = block_height
        self.block_hash = block_hash
        self.allocated_balances = allocated_balances

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> AssetResponse:
        return cls(
            data.get('id'),
            data.get('total'),
            data.get('balance'),
            data.get('lockedAmount'),
            data.get('available'),
            data.get('pending'),
            data.get('selfStakedCPU'),
            data.get('selfStakedNetwork'),
            data.get('pendingRefundCPU'),
            data.get('pendingRefundNetwork'),
            data.get('totalStakedCPU'),
            data.get('totalStakedNetwork'),
            BalanceRewardInfo.deserialize(data.get('rewardInfo', {})),
            data.get('blockHeight'),
            data.get('blockHash'),
            AllocatedBalances.deserialize(data.get('allocatedBalances', {}))
        )
