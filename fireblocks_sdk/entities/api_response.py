from typing import Dict, TypeVar, Generic

T = TypeVar('T')


class ApiResponse(Generic[T]):
    def __init__(self, status_code: int, content, extras: Dict[str, str]) -> None:
        self.status_code = status_code
        self.content = content
        self.extras = extras
