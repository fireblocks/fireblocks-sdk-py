from __future__ import annotations

from abc import abstractmethod
from typing import Dict, TypeVar, Generic

T = TypeVar('T')


class Deserializable(Generic[T]):
    @classmethod
    @abstractmethod
    def deserialize(cls: T, data: Dict[str, any]) -> T:
        pass
