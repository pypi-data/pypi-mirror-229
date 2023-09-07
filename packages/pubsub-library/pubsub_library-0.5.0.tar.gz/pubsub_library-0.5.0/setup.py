from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="pubsub_library",
    version="0.5.0",
    description="Lib para gerenciar filas de mensagens",
    author="Caiqui Fhelipe",
    author_email="caiqui_lipe@hotmail.com",
    url="https://github.com/caiquilipe/pubsub-library.git",
    packages=find_packages(),
    install_requires=requirements,
)
