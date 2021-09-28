# Heating Control

## Overview

For this task, you will need to prototype a simple heating control service.

Imagine that you have a single room with a few temperature sensors installed there and a radiator valve you can control.

Your task is to keep the room temperature at 22°C by setting the valve openness from 0 (fully closed) to 100 (fully open). The current room temperature is indicated by sensor readings.

The temperature sensors send the readings periodically to the mqtt topic. You can set the valve openness by sending a specific message to a specific mqtt topic.


### Input

You get the periodic temperature readings on the topic `/readings/temperature` in the json format:


```json
{
  "sensorID": "sensor-1",
  "type": "temperature",
  "value": 25.3
}
```

Receiving this message should indicate that Sensor 1 reads 25.3°C for the area of the room where it has been installed.


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


## Prerequisites

You need:
- Python 3.9 (not tested below 3.9, but it should be fine with 3.8)
- [Poetry](https://python-poetry.org/) (Python packaging manager)
- MSQTT service like Mosquitto

If you don't want to use Poetry but want to install Python dependencies manually, you will need the following Python packages:
- fastapi
- fastapi_mqtt
- toml

## To run without Docker

Edit the config file `config.py` to change the MQTT credentials if necessary. 

Launch MQTT service.
	On MacOS, as a one-time executable:
```sh
/usr/local/opt/mosquitto/sbin/mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf
```
	or, on MacOS, as a service:
```sh
brew services start mosquitto
```

Then, to run, just do:
	```sh
	poetry run uvicorn app.main:app --reload
	```
Poetry will create the virtual environment and install the necessary packages in it for you.

### Example MQTT message
```sh
mosquitto_pub -t /mqtt -m "Hello World" -u "username" -P "password"
```

## To run with Docker

Build the image from the Dockerfile with:
```sh
docker build -t heating-control-image .
```

Run it with:
```sh
docker run -d --name heating-control -p 80:80 heating-control-image
```

We can also run to Mosquitto container with:
```sh
docker run -it -p 1883:1883 --name=mosquitto toke/mosquitto
```


## File structure

- `/data/`
	- `example-imput.json`: the input JSON

- `/app/`
	- `main.py`: the main function of the script, where everything starts
	- `config.py`: configuration file to be edited
	- `helpers.py`: secondary helper functions used by `main.py`
