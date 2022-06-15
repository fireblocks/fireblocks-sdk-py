from __future__ import annotations

from typing import Dict


class OperationSuccessResponse:
    def __init__(self, success: bool) -> None:
        self.success = success

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> OperationSuccessResponse:
        return cls(data.get('success'))
