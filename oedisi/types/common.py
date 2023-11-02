from pydantic import BaseModel
from typing import Dict

BASE_DOCKER_IMAGE = "python:3.10.6-slim-bullseye"
BROKER_SERVICE = "broker"
APP_NAME = "oedisi"
DOCKER_HUB_USER = "aadillatif"

class BrokerConfig(BaseModel):
    broker_port : int = 23404
    broker_ip : str = "10.5.0.2"
    api_port : int = 12345
    services : Dict = {}