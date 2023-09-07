from setuptools import setup, find_packages


setup(
    name="pubsub_library",
    version="0.7.0",
    description="Lib para gerenciar filas de mensagens",
    author="Caiqui Fhelipe",
    author_email="caiqui_lipe@hotmail.com",
    url="https://github.com/caiquilipe/pubsub-library.git",
    packages=find_packages(),
    install_requires=[
        "aio-pika",
        "aioredis",
        "azure-core",
        "azure-servicebus",
    ],
)
