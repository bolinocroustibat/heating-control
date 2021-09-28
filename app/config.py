# from fastapi.logger import logger
# import logging
import toml

DESIRED_ROOM_TEMP: float = 22.0

# App name, version, description
config: dict = toml.load("./pyproject.toml")
APP_NAME: str = config["tool"]["poetry"]["name"]
VERSION: str = config["tool"]["poetry"]["version"]
DESCRIPTION: str = config["tool"]["poetry"]["description"]

# MQTT
MQTT_HOST: str = "127.0.0.1"
MQTT_PORT: int = 1883
MQTT_USERNAME: str = "username"
MQTT_PASSWORD: str = "password"

# # Logging
# formatter = logging.Formatter(
#     "[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s", "%Y-%m-%d %H:%M:%S")
# # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler = logging.StreamHandler()
# handler.setFormatter(formatter)

# logger.addHandler(handler)

# logger.error("Logging initialized")
