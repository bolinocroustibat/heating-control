# Heating Control

## Overview

This app keeps the temperatures of rooms at a desired one defined in `config.py` (default is 22°C) by subscribing to MQTT messages from the rooms temperature and motion sensors, and publishing a MQTT message to the rooms heating valves.

The current state of all the rooms temperature and presence is stored in a global variable for the app called `state`.

Only if motion is detected in the room, or if the motion sensor didn't return any information, the temperature will be adjusted.

If no motion is detected, the heating valve is closed.


## Stack

It uses [FastAPI](https://fastapi.tiangolo.com/), a very modern and beautifully designed Python API framework based on Python type hinting and Pydantic models, and [FastApi-MQTT](https://sabuhish.github.io/fastapi-mqtt/), a MQTT implementation module for FastAPI. See [Run without Docker->Prerequisites](####prerequisites) section for more details.


## Suggested improvements

### Improvement #1
**Issue:**
Currently the app has no unit tests.

**Suggested improvement:**
Unit tests can be easily added in a `app/test.py` file, following FastAPI test standards (https://fastapi.tiangolo.com/tutorial/testing/).

### Improvement #2
**Issue:**
Currently, the state for rooms temperatures and motions is not stored elsewhere than the app memory, so if the app is stopped and restarted for example, state will be lost and it will need to wait for the next reading from sensors to adjust the temperature.

**Suggested improvement:**
Store the state in a persistent database like a local SQLite or a NoSQL like MongoDB.

### Improvement #3
**Issue:**
Currently, the app can only fully open (100) or fully close (0) the heating valves, so it has no way to change the heating rate. If the time between two readings is too long for example, the app might overshoot the desired temperature.

**Suggested improvement:**
When the current temperature is close to the desired temperature, the valve could open not fully (any value between 0 and 100), according to a proper algorithm. By storing the datetime for the previous reading(s) from sensors, the algorithm could calculate the past growth rate of the temperature between the last readings with a basic linear regression, and use that to adjust the next valve opening rate.

### Improvement #4
**Suggested improvement:**
Use instanciated objects from a `Room` class with temperature and motion attributes instead of a global dictionary variable for the state.


## Configuration

Edit the config file `app/config.py` to change:
- the desired room temperature (`DESIRED_ROOM_TEMP`)
- the MQTT credentials if necessary


## HTTP endpoints

- `/health-check`:
	- Returns information about that health of the app, including the current state of all rooms, and the connection status to MQTT broker
	- Method: `GET`
- `/docs`:
	- Returns the OpenAPI specification of the service
	- Method: `GET`


## Topics

- `/readings/temperature`
	Example input:
	```json
	{
	"sensorID": "sensor-3",
	"type": "temperature",
	"value": 25.3
	}

- `/readings/motion`
	Example input:
	```json
	{
	"sensorID": "sensor-2",
	"type": "motion",
	"value": true
	}

- `/actuators/room-{room_id}`
	Example output:
	```json
	{
	"level": 100
	}
	```


## How to run

### Run with Docker

Run all the containers (MQTT broker + app) with:
```sh
docker-compose up -d
```

### Run without Docker

#### Prerequisites

You need:
- Python 3.9 (not tested below 3.9, but it should be fine with 3.8)
- [Poetry](https://python-poetry.org/) (Python packaging manager)
- a MQTT broker like [Mosquitto](https://mosquitto.org/:)

If you don't want to use Poetry but want to install Python dependencies manually, you will need the following Python packages:
- [FastAPI](https://fastapi.tiangolo.com/)
- [FastApi-MQTT](https://sabuhish.github.io/fastapi-mqtt/)
- toml

#### Run the app

Run Mosquitto MQTT broker with:
-oOn MacOS, as a one-time executable:
```sh
/usr/local/opt/mosquitto/sbin/mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf
```
- or, on MacOS, as a service:
```sh
brew services start mosquitto
```
- if you don't want to install Mosquitto, we can also run a Mosquitto container with:
```sh
docker run -it -p 1883:1883 --name=mosquitto toke/mosquitto
```

Then run the app with:
```sh
poetry run uvicorn app.main:app --reload
```
Poetry will create the virtual environment and install the necessary packages in it for you.

You can then send a message to the MQTT broker in another terminal windows like this:
```sh
mosquitto_pub -t /readings/temperature -m "{"sensorID": "sensor-3", "type": "temperature", "value": 25.3 }" -u "username" -P "password"
```
