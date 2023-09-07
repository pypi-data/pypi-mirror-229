from pubsub_library.interfaces.pubsub import PubSubInterface
from typing import Callable
import aio_pika
import aio_pika.abc
import logging


class RabbitMQPubSub(PubSubInterface):
    def __init__(self, connection_string: str) -> None:
        self.__connection_string = connection_string
        self.__logger = logging.getLogger(__name__)

    async def __aenter__(self) -> "RabbitMQPubSub":
        self.__connection = await aio_pika.connect_robust(
            self.__connection_string
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return None

    async def publish(self, queue_name: str, message: bytes):
        try:
            async with self.__connection:
                channel = await self.__connection.channel()
                await channel.default_exchange.publish(
                    aio_pika.Message(body=message),
                    routing_key=queue_name,
                )
        except Exception as e:
            self.__logger.error(f"Error publishing message: {e}")
            raise Exception("Error publishing message")

    async def subscribe(
        self, queue_name: str, callback: Callable[[bytes], None]
    ):
        try:
            async with self.__connection:
                channel = await self.__connection.channel()
                queue = await channel.declare_queue(
                    queue_name, auto_delete=True
                )
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            await callback(message.body)
        except Exception as e:
            self.__logger.error(f"Error receiving message: {e}")
            raise Exception("Error receiving message")
