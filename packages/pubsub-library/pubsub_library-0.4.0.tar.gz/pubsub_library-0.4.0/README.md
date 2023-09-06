# PubSub Library

Uma biblioteca Python flexível para comunicação de publicação e assinatura (pub/sub) usando diferentes sistemas de mensagens.

## Instalação

Escolha o repositório que você deseja usar para a instalação.

### Instalação via PyPI

```bash
pip install pubsub-library
```

### Instalação via GitHub (Azure Service Bus)

```bash
pip install -e git+https://github.com/caiquilipe/pubsub-library.git@azure-service-bus#egg=pubsub-library
```

### Instalação via GitHub (Redis)

```bash
pip install -e git+https://github.com/caiquilipe/pubsub-library.git@redis#egg=pubsub-library
```

### Instalação via GitHub (RabbitMQ)

```bash
pip install -e git+https://github.com/caiquilipe/pubsub-library.git@rabbitmq#egg=pubsub-library
```

## Uso

### Exemplo de Uso (Azure Service Bus)

```python
from pubsub_library import AzurePubSub

bus = AzurePubSub(connection_string="SUA_CONNECTION_STRING")
async with bus:
    await bus.publish("canal_teste", b"Mensagem de exemplo")

async with bus:
    await bus.subscribe("canal_teste", callback_function)
```

### Exemplo de Uso (Redis)

```python
from pubsub_library import RedisPubSub

bus = RedisPubSub(connection_string="SUA_CONNECTION_STRING")

async with bus:
    await bus.publish("canal_teste", b"Mensagem de exemplo")

async with bus:
    await bus.subscribe("canal_teste", callback_function)
```

### Exemplo de Uso (RabbitMQ)

```python
from pubsub_library import RabbitMQPubSub

bus = RabbitMQPubSub(connection_string="SUA_CONNECTION_STRING")

async with bus:
    await bus.publish("canal_teste", b"Mensagem de exemplo")

async with bus:
    await bus.subscribe("canal_teste", callback_function)
```