from pydantic.v1 import BaseModel
from typing import Dict, Optional
from enum import Enum

BASE_DOCKER_IMAGE = "python:3.10.6-slim-bullseye"
BROKER_SERVICE = "broker"
APP_NAME = "oedisi"
DOCKER_HUB_USER = "aadillatif"
KUBERNETES_SERVICE_NAME = "oedisi-service"


class DefaultFileNames(str, Enum):
    INPUT_MAPPING = "input_mapping.json"
    STATIC_INPUTS = "static_inputs.json"


class BrokerConfig(BaseModel):
    broker_port: int = 23404
    broker_ip: str = "10.5.0.2"
    api_port: int = 12345
    feeder_host: str | None = None
    feeder_port: int | None = None



class HeathCheck(BaseModel):
    hostname: str
    host_ip: str


class ServerReply(BaseModel):
    detail: str
    action: Optional[str]
