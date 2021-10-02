# from fastapi.logger import logger
# import logging
import toml


DESIRED_ROOM_TEMP: float = 22.0

# App name, version, description
try:
    # Inside Docker
    config: dict = toml.load("/code/pyproject.toml")
except FileNotFoundError:
    # Outside Docker
    config: dict = toml.load("./pyproject.toml")
APP_NAME: str = config["tool"]["poetry"]["name"]
VERSION: str = config["tool"]["poetry"]["version"]
DESCRIPTION: str = config["tool"]["poetry"]["description"]

# MQTT
MQTT_PORT: int = 1883
MQTT_USERNAME: str = "username"
MQTT_PASSWORD: str = "password"
