from __future__ import annotations

from typing import Dict


class CreateTransactionResponse:

    def __init__(self, id: str, status: str) -> None:
        super().__init__()
        self.id = id
        self.status = status

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> CreateTransactionResponse:
        return cls(data.get('id'), data.get('status'))
