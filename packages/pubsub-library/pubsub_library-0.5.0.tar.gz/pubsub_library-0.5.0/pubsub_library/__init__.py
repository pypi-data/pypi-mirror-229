from pubsub_library.repositories.rabbitmq import RabbitMQPubSub
from pubsub_library.repositories.service_bus import AzurePubSub
import logging

logging.basicConfig(
    level=logging.WARNING,  # Defina o nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


__all__ = [
    "RabbitMQPubSub",
    "AzurePubSub",
]
