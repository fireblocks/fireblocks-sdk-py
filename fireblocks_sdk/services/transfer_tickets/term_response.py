from __future__ import annotations

from typing import List, Dict

from fireblocks_sdk.entities.deserializable import Deserializable, T


class TermResponse(Deserializable):

    def __init__(self, term_id: str, network_connection_id: str, outgoing: str, asset: str,
                 amount: str, txt_ids: List[str], status: str, note: str) -> None:
        super().__init__()
        self.term_id = term_id
        self.network_connection_id = network_connection_id
        self.outgoing = outgoing
        self.asset = asset
        self.amount = amount
        self.txt_ids = txt_ids
        self.status = status
        self.note = note

    @classmethod
    def deserialize(cls: T, data: Dict) -> TermResponse:
        return cls(
            data.get('termId'),
            data.get('networkConnectionId'),
            data.get('outgoing'),
            data.get('asset'),
            data.get('amount'),
            data.get('txIds'),
            data.get('status'),
            data.get('note'),
        )
