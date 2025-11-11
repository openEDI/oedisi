import traceback
import uvicorn
import logging
import socket
import json
import os

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from oedisi.componentframework.system_configuration import ComponentStruct
from oedisi.types.common import ServerReply, HeathCheck, DefaultFileNames
from oedisi.types.common import BrokerConfig

from component1 import TestFederate

app = FastAPI()

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

@app.get("/")
def read_root():
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    response = HeathCheck(hostname=hostname, host_ip=host_ip).dict()
    return JSONResponse(response, 200)


@app.post("/run")
async def run_model(broker_config: BrokerConfig, background_tasks: BackgroundTasks):
    logger.info("Running componenet 1")
    try:
        logger.info("Creating federate 1")
        federate = TestFederate(broker_config)
        logger.info("Federate 1 created")
        background_tasks.add_task(federate.run)
        logger.info("Federate 1 started")
        return {"reply": "success", "error": False}
    except Exception as e:
        return {"reply": str(e), "error": True}


@app.post("/configure/")
async def configure(component_struct:ComponentStruct): 
    component = component_struct.component
    params = component.parameters
    params["name"] = component.name
    links = {}
    for link in component_struct.links:
        links[link.target_port] = f"{link.source}/{link.source_port}"
    json.dump(links , open(DefaultFileNames.INPUT_MAPPING.value, "w"))
    json.dump(params , open(DefaultFileNames.STATIC_INPUTS.value, "w"))
    response = ServerReply(
            detail = f"Sucessfully updated configuration files."
        ).dict() 
    return JSONResponse(response, 200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
