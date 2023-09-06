from abc import ABC, abstractmethod
from typing import Callable


class PubSubInterface(ABC):
    @abstractmethod
    def __init__(self, connection_string: str) -> None:
        raise NotImplementedError("constructor method not implemented")

    @abstractmethod
    async def publish(self, queue_name: str, message: bytes) -> None:
        raise NotImplementedError("publish method not implemented")

    @abstractmethod
    async def subscribe(
        self, queue_name: str, callback: Callable[[bytes], None]
    ) -> None:
        raise NotImplementedError("subscribe method not implemented")

    @abstractmethod
    async def __aenter__(self) -> "PubSubInterface":
        raise NotImplementedError("enter method not implemented")

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError("exit method not implemented")
