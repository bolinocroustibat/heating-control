import asyncio
import json
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.security import HTTPBasicCredentials
from fastapi_mqtt import FastMQTT, MQTTConfig

from app.config import (
    APP_NAME,
    DESCRIPTION,
    VERSION,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    DESIRED_ROOM_TEMP,
)


# Register FastAPI main app
app = FastAPI(title=APP_NAME, description=DESCRIPTION, version=VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


mqtt_config = MQTTConfig(
    host=MQTT_HOST,
    port=MQTT_PORT,
    keepalive=60,
    username=MQTT_USERNAME,
    password=MQTT_PASSWORD,
)

mqtt = FastMQTT(config=mqtt_config)
mqtt.init_app(app)


state: dict = {}


@app.get("/health-check")
async def health_check() -> dict:
    """
    Display basic health check
    """
    try:
        if mqtt.client.is_connected:
            return {"mqtt status": "ok"}
        else:
            return {"mqtt status": "not connected"}
    except:
        return {"mqtt status": "unknown error"}


@mqtt.on_connect()
def connect(client, flags: int, rc: int, properties: dict) -> None:
    mqtt.client.subscribe(
        "/readings/temperature"
    )  # subscribe to MQTT topic from temperature sensors
    mqtt.client.subscribe(
        "/readings/motion"
    )  # subscribe to MQTT topic from motion sensors
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None) -> None:
    print("Disconnected")


@mqtt.on_subscribe()
def subscribe(client, mid: int, qos: Tuple, properties: dict) -> None:
    print("Subscribed", client, mid, qos, properties)


@mqtt.on_message()
async def message(
    client, topic: str, payload: bytes, qos: int, properties: dict
) -> None:
    if topic == "/readings/temperature":
        try:
            message: dict = json.loads(payload.decode("utf-8"))
            sensor_id: str = message["sensorID"]
            room_id: int = sensor_id.split("-")[1]
            # message_type: str = message["type"] # useless here
            value: float = message["value"]
        except:
            raise HTTPException(status_code=400, detail="MQTT message error")

        if room_id not in state:
            state[room_id] = {"temperature": value}
        else:
            state[room_id]["temperature"] = value

        print(
            f"Current temperature report for room {room_id} updated to {str(value)}°C. Current state: {str(state)}"
        )

        await update_valves(state=state)

    if topic == "/readings/motion":
        try:
            message: dict = json.loads(payload.decode("utf-8"))
            sensor_id: str = message["sensorID"]
            room_id: int = sensor_id.split("-")[1]
            # message_type: str = message["type"] # useless here
            value: bool = message["value"]
        except:
            raise HTTPException(status_code=400, detail="MQTT message error")

        if room_id not in state:
            state[room_id] = {"motion": value}
        else:
            state[room_id]["motion"] = value

        print(
            f"Current motion report for room {room_id} updated to {str(value)}. Current state: {str(state)}"
        )

        await update_valves(state=state)


async def update_valves(state: dict) -> None:
    for room_id, state in state.items():
        if state.get("motion", True): # if motion is detected, or if the motion sensor has no state (broken, or no info yet)
            if state["temperature"] < DESIRED_ROOM_TEMP:
                await open_valve(room_id=room_id)
            else:
                await close_valve(room_id=room_id)
        else:
            await close_valve(room_id=room_id)


async def open_valve(room_id: int) -> None:
    mqtt.publish(f"/actuators/room-{room_id}/set", json.dumps({"value": 100}))


async def close_valve(room_id: int) -> None:
    mqtt.publish(f"/actuators/room-{room_id}/set", json.dumps({"value": 0}))
