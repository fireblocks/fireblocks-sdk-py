from __future__ import annotations

from typing import Dict


class CreateTransferTicketResponse:
    def __init__(self, ticket_id: str) -> None:
        self.ticket_id = ticket_id

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> CreateTransferTicketResponse:
        return cls(data.get('ticketId'))
