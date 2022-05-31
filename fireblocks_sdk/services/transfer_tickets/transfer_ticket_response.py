from __future__ import annotations

from typing import Dict, List

from fireblocks_sdk.entities.deserializable import Deserializable, T
from fireblocks_sdk.services.transfer_tickets.term_response import TermResponse


class TransferTicketResponse(Deserializable):

    def __init__(self, ticket_id: str, external_ticket_id: str, description: str, status: str,
                 terms: List[TermResponse]) -> None:
        super().__init__()
        self.ticket_id = ticket_id
        self.external_ticket_id = external_ticket_id
        self.description = description
        self.status = status
        self.terms = terms

    @classmethod
    def deserialize(cls: T, data: Dict) -> TransferTicketResponse:
        return cls(
            data.get('ticketId'),
            data.get('externalTicketId'),
            data.get('description'),
            data.get('status'),
            [TermResponse.deserialize(term) for term in data.get('terms')]
        )
