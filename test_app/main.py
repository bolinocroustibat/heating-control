import json
import os

# from time import sleep
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mqtt import FastMQTT, MQTTConfig
import requests

from app.config import (
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    DESIRED_ROOM_TEMP,
)


TEST_ROOM_ID: int = 1


# Register FastAPI main app
test_app = FastAPI(
    title="test_app", description="test_app_description", version="0.1.0"
)

test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


mqtt_config = MQTTConfig(
    host=os.getenv(
        "MQTT_HOST", "127.0.0.1"
    ),  # Get the MQTT host from the environment if Docker, otherwise use localhost
    port=MQTT_PORT,
    keepalive=60,
    username=MQTT_USERNAME,
    password=MQTT_PASSWORD,
)

mqtt = FastMQTT(config=mqtt_config)
mqtt.init_app(test_app)


@mqtt.on_connect()
def connect(client, flags: int, rc: int, properties: dict) -> None:
    mqtt.client.subscribe(
        f"/actuators/room-{TEST_ROOM_ID}/set"
    )  # subscribe to MQTT topic from temperature sensors
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None) -> None:
    print("Disconnected")


@mqtt.on_subscribe()
def subscribe(client, mid: int, qos: Tuple, properties: dict) -> None:
    print("Subscribed", client, mid, qos, properties)


@test_app.get("/test")
async def end_to_end_test() -> dict:
    """
    Send a test message to the MQTT broker, and read the health-checl to control if the state has been changed
    """
    test_current_temp: float = 10
    test_motion = True
    mqtt.publish(
        "/readings/temperature",
        json.dumps(
            {
                "sensorID": f"sensor-{TEST_ROOM_ID}",
                "type": "temperature",
                "value": str(test_current_temp),
            }
        ),
    )
    mqtt.publish(
        "/readings/motion",
        json.dumps(
            {
                "sensorID": f"sensor-{TEST_ROOM_ID}",
                "type": "motion",
                "value": test_motion,
            }
        ),
    )
    # Make a GET request to health check endpoint
    # sending get request and saving the response as response object
    req = requests.get(url="http://127.0.0.1:8000/health-check")
    response: dict = req.json()
    read_state = response["state"][str(TEST_ROOM_ID)]

    # Build the test response
    response: dict = {"result": "Test failed"}
    if (read_state["temperature"] == str(test_current_temp)) and (
        read_state["motion"] == test_motion
    ):
        response["result"] = "Test passed"
    response["read_state"] = read_state
    return response
