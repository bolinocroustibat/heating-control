# Heating Control

## Overview

This app keeps the temperatures of rooms at a desired one defined in `config.py` (default is 22°C) by subscribing to MQTT messages from the rooms temperature and motion sensors, and publishing a MQTT message to the rooms heating valves.

The current state of all the rooms temperature and presence is stored in a global variable for the app called `state`.

Only if motion is detected in the room, or if the motion sensor didn't return any information, the temperature will be adjusted.

If no motion is detected, the heating valve is closed.


## Suggested improvements

1)
**Issue:**
Currently, the state for rooms temperatures and motions is not stored elsewhere than the app memory, so if the app is stopped and restarted for example, state will be lost and it will need to wait for the next reading from sensors to adjust the temperature.

**Suggested improvement:**
Store the state in a persistent database like a local SQLite or a NoSQL like MongoDB.

2)
**Issue:**
Currently, the app can only fully open (100) or fully close (0) the heating valve, so it has no way to change the heating rate. If the time between two readings is too long for example, the app might overshoot the desired temperature.

**Suggested improvement:**
When the current temperature is close to the desired temperature, the valve could open not fully (between O and 100), according to a proper algorithm. By storing the datetime for the previous reading(s) from sensors, the algorithm could calculate the past growth rate of the temperature between the last readings with a basic linear regression, and use that to adjust the next valve opening rate.


### Input

Edit the config file `app/config.py` to change:
- the desired room temperature (`DESIRED_ROOM_TEMP`)
- the MQTT broker credentials, if necessary



- `/health-check`: returns some info about the app, including if MQTT service is running
- `/docs`: returns the OpenAPI specification of the app

Receiving this message should indicate that Sensor 1 reads 25.3°C for the area of the room where it has been installed.

## MQTT topics

### Output

You will need to send the valve openness value to the topic `/actuators/room-1` in the json format:

```json
{
  "level": 14
}
```

Sending the message indicates that the valve should be set to 14% openness.


### Hints
- Use `docker` and `docker-compose` to orchestrate your solution
- The fastest way to get mqtt broker is to run mosquitto with docker:
    ```
    docker run -it -p 1883:1883 --name=mosquitto  toke/mosquitto
    ```
- You don't need to use fancy algorithms for temperature control; opt for something simple. If you want, you can describe a more complex solution in the README.


### Too easy?

If you finished the task quickly and feel like doing more (that's completely optional):
- You can imagine that there's also a motion sensor and you want to keep the room warm only when motion is present.
- You can imagine there are a lot of rooms! And the sensors and valves should be controlled on per room basis.
- You can imagine any other limitations you think would be fun to work with.


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
- fastapi
- fastapi_mqtt
- toml

#### Run the app

Run Mosquitto MQTT broker with:
	- On MacOS, as a one-time executable:
	```sh
	/usr/local/opt/mosquitto/sbin/mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf
	```
	- or, on MacOS, as a service:
	```sh
	brew services start mosquitto
	```

If you don't want to install Mosquitto, we can also run a Mosquitto container with:
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
