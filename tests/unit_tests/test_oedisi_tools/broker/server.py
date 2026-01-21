from fastapi import FastAPI, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

import helics as h
import httpx

from functools import cache
from pathlib import Path
import traceback
import requests
import uvicorn
import logging
import asyncio
import socket
import time
import json
import os

from oedisi.componentframework.system_configuration import (
    ComponentStruct,
    WiringDiagram,
)
from oedisi.types.common import ServerReply, HeathCheck

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

BASE_PATH = Path(__file__).parent
os.chdir(BASE_PATH)
app = FastAPI()

WIRING_DIAGRAM_FILENAME = "system.json"
WIRING_DIAGRAM: WiringDiagram | None = None


def read_settings():
    broker_host = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # connect to Google DNS (no actual data sent)
        broker_ip = s.getsockname()[0]
    finally:
        s.close()
    api_port = 8766  # int(os.environ['PORT'])

    component_map = {broker_host: api_port}
    if WIRING_DIAGRAM:
        for component in WIRING_DIAGRAM.components:
            component_map[component.host] = component.container_port
    else:
        raise HTTPException(
            status_code=404,
            detail="Use the '/configure' setpoint to setup up the WiringDiagram before making requests other enpoints",
        )

    return component_map, broker_ip, api_port


@cache
def kubernetes_service():
    if "KUBERNETES_SERVICE_NAME" in os.environ:
        return os.environ["KUBERNETES_SERVICE_NAME"]  # works with kurenetes
    elif "SERVICE_NAME" in os.environ:
        return os.environ["SERVICE_NAME"]  # works with minikube
    else:
        return None


def build_url(host: str, port: int, enpoint: list):
    if kubernetes_service():
        url = f"http://{host}.{kubernetes_service()}:{port}/"
    else:
        url = f"http://{host}:{port}/"
    url = url + "/".join(enpoint) + "/"
    return url


async def run_simulation():
    component_map, broker_ip, api_port = read_settings()
    logger.info(f"{broker_ip}, {api_port}")
    initstring = f"-f {len(component_map)-1} --name=mainbroker --loglevel=trace --local_interface={broker_ip} --localport=23404"
    logger.info(f"Broker initaialization string: {initstring}")
    broker = h.helicsCreateBroker("zmq", "", initstring)

    app.state.broker = broker
    logger.info(f"Created broker: {broker}")

    isconnected = h.helicsBrokerIsConnected(broker)
    logger.info(f"Broker connected: {isconnected}")
    logger.info(str(component_map))
    broker_host = socket.gethostname()
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = []
        for service_ip, service_port in component_map.items():
            if service_ip != broker_host:
                url = build_url(service_ip, service_port, ["run"])
                logger.info(f"service_ip: {service_ip}, service_port{service_port}")
                logger.info(f"making a request to url - {url}")

                myobj = {
                    "broker_port": 23404,
                    "broker_ip": broker_ip,
                    "api_port": api_port,
                }
                logger.info(f"{myobj}")
                # create tasks so we can monitor them periodically
                task = asyncio.create_task(client.post(url.removesuffix("/"), json=myobj))
                tasks.append(task)

        if tasks:
            pending = set(tasks)
            while pending:
                done = {t for t in pending if t.done()}
                for idx, t in enumerate(tasks):
                    state = (
                        "done" if t.done() else "cancelled" if t.cancelled() else "pending"
                    )
                    info = None
                    if t.done() and not t.cancelled():
                        try:
                            res = t.result()
                            info = f"status_code={getattr(res, 'status_code', 'N/A')}"
                        except Exception as exc:
                            info = f"exception={exc}"
                    logger.info(f"Task {idx}: {state} {info or ''}")

                # remove completed tasks from pending
                pending -= done

                if pending:
                    await asyncio.sleep(5)
                else:
                    # ensure exceptions are observed to avoid warnings
                    for idx, t in enumerate(tasks):
                        try:
                            res = t.result()
                            logger.info(
                                f"Task {idx} succeeded: {getattr(res, 'status_code', 'N/A')}"
                            )
                        except Exception as exc:
                            logger.error(f"Task {idx} failed: {exc}")

    while h.helicsBrokerIsConnected(broker):
        time.sleep(1)
        query_result = broker.query("broker", "current_state")
        logger.info(f"Federates expected: {len(component_map)-1}")
        logger.info(f"Federates connected: {len(broker.query("broker", "federates"))}")
        logger.info(f"Simulation state: {query_result['state']}")
        logger.info(f"Global time: {query_result['attributes']['parent']}")
    h.helicsCloseLibrary()
    return


@app.get("/")
def read_root():
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    response = HeathCheck(hostname=hostname, host_ip=host_ip).model_dump()
    return JSONResponse(response, 200)


@app.post("/run/")
async def run_feeder(background_tasks: BackgroundTasks):
    logger.info("Run Called on Broker service")
    try:
        background_tasks.add_task(run_simulation)
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(status_code=404, detail=str(err))


@app.post("/configure/")
async def configure(wiring_diagram: WiringDiagram):
    logger.info("Configure Called on Broker service")
    global WIRING_DIAGRAM
    WIRING_DIAGRAM = wiring_diagram
    logger.info(f"Writing wiring diagram: {WIRING_DIAGRAM_FILENAME}")
    json.dump(wiring_diagram.model_dump(), open(WIRING_DIAGRAM_FILENAME, "w"))
    for component in wiring_diagram.components:
        component_model = ComponentStruct(component=component, links=[])
        for link in wiring_diagram.links:
            if link.target == component.name:
                component_model.links.append(link)

        url = build_url(component.host, component.container_port, ["configure"])
        logger.info(f"making a request to url - {url}")

        r = requests.post(url, json=component_model.model_dump())
        assert (
            r.status_code == 200
        ), f"POST request to update configuration failed for url - {url}"
    return JSONResponse(
        ServerReply(
            detail="Sucessfully updated config files for all containers"
        ).model_dump(),
        200,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
