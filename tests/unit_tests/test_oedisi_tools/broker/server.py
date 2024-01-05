from fastapi import FastAPI, BackgroundTasks, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

from pathlib import Path

import helics as h
import grequests
import traceback
import uvicorn
import logging
import socket
import time
import yaml
import sys
import os

BASE_PATH = Path(__file__).parent
os.chdir(BASE_PATH)
app = FastAPI()


def read_settings():
    component_map = {}
    yaml_file = BASE_PATH / "docker-compose.yml"
    assert yaml_file.exists(), f"{yaml_file} does not exist"
    with open(yaml_file, "r") as stream:
        config = yaml.safe_load(stream)
    services = config["services"]
    print(services)
    broker = services.pop("oedisi_broker")
    broker_ip = broker["networks"]["custom-network"]["ipv4_address"]
    api_port = int(broker["ports"][0].split(":")[0])

    for service in services:
        ip = services[service]["networks"]["custom-network"]["ipv4_address"]
        port = int(services[service]["ports"][0].split(":")[0])
        component_map[ip] = port

    return services, component_map, broker_ip, api_port


def run_simulation(services, component_map, broker_ip, api_port):
    initstring = f"-f {len(component_map)} --name=mainbroker --loglevel=trace --local_interface={broker_ip} --localport={23404}"
    logging.info(f"Broker initaialization string: {initstring}")
    broker = h.helicsCreateBroker("zmq", "", initstring)
    logging.info(broker)
    isconnected = h.helicsBrokerIsConnected(broker)
    logging.info(f"Broker connected: " + str(isconnected))
    logging.info(str(component_map))
    replies = []
    for service_ip, service_port in component_map.items():
        url = f"http://{service_ip}:{service_port}/run/"
        print(url)
        myobj = {
            "broker_port": 23404,
            "broker_ip": broker_ip,
            "api_port": api_port,
            "services": services,
        }
        replies.append(grequests.post(url, json=myobj))

    print(grequests.map(replies))
    return


@app.get("/")
def read_root():
    hostname = socket.gethostname()
    host_ip = "127.0.0.1"
    try:
        host_ip = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        try:
            host_ip = socket.gethostbyname(socket.gethostname() + ".local")
        except socket.gaierror:
            pass
    return {"hostname": hostname, "host_ip": host_ip}


@app.post("/run")
async def run_feeder(background_tasks: BackgroundTasks):
    try:
        data_input = read_settings()
        background_tasks.add_task(run_simulation, *data_input)
    except Exception as e:
        err = traceback.format_exc()
        raise HTTPException(status_code=404, detail=str(err))


if __name__ == "__main__":
    port = int(sys.argv[2])
    uvicorn.run(app, host="0.0.0.0", port=port)
