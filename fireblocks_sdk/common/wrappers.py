import functools
from typing import TypeVar

from fireblocks_sdk.entities.deserializable import Deserializable

T = TypeVar('T')


def response_deserializer(response_type: T) -> T:
    def inner(func) -> T:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return_value = func(*args, **kwargs)
            if isinstance(return_value, list):
                return [response_type.deserialize(item) for item in return_value]

            if not issubclass(response_type, Deserializable):
                return return_value

            return response_type.deserialize(return_value)

        return wrapper

    return inner
