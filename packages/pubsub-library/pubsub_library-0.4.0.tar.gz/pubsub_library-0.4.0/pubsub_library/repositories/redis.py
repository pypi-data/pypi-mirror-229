from pubsub_library.interfaces.pubsub import PubSubInterface
from typing import Callable
import aioredis
import logging


class RedisPubSub(PubSubInterface):
    def __init__(self, connection_string: str) -> None:
        self.__redis = aioredis.from_url(connection_string)
        self.__pubsub = self.__redis.pubsub()
        self.__logger = logging.getLogger(__name__)

    async def __aenter__(self) -> "RedisPubSub":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.__redis.close()

    async def publish(self, queue_name: str, message: bytes) -> None:
        try:
            await self.__redis.publish(queue_name, message)
        except Exception as e:
            self.__logger.error(f"Error publishing message: {e}")
            raise Exception("Error publishing message")

    async def subscribe(
        self, queue_name: str, callback: Callable[[bytes], None]
    ) -> None:
        try:
            await self.__pubsub.subscribe(queue_name)
            async for message in self.__pubsub.listen():
                await callback(message)
        except Exception as e:
            self.__logger.error(f"Error receiving message: {e}")
            await self.__pubsub.unsubscribe(queue_name)
            raise Exception("Error receiving message")
