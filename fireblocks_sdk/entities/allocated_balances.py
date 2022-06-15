from __future__ import annotations

from typing import Dict, Union


class AllocatedBalances:
    def __init__(self, allocation_id: str, total: str, available: str, third_party_account_id: Union[str, None],
                 affiliation: Union[str, None], virtual_type: Union[str, None], pending: Union[str, None],
                 frozen: Union[str, None], locked: Union[str, None]) -> None:
        self.virtual_type = virtual_type
        self.total = total
        self.available = available
        self.pending = pending
        self.frozen = frozen
        self.locked = locked
        self.affiliation = affiliation
        self.third_party_account_id = third_party_account_id
        self.allocation_id = allocation_id

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> AllocatedBalances:
        return cls(
            data.get('allocationId'),
            data.get('total'),
            data.get('available'),
            data.get('thirdPartyAccountId'),
            data.get('affiliation'),
            data.get('virtualType'),
            data.get('pending'),
            data.get('frozen'),
            data.get('locked')
        )
