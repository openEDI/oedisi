from typing import Dict, Optional
from pydantic import BaseModel
from enum import Enum
import warnings

BASE_DOCKER_IMAGE = "python:3.10.6-slim-bullseye"
BROKER_SERVICE = "broker"
APP_NAME = "oedisi"
DOCKER_HUB_USER = "aadillatif"
KUBERNETES_SERVICE_PREFIX= "svc"


class DefaultFileNames(str, Enum):
    INPUT_MAPPING = "input_mapping.json"
    STATIC_INPUTS = "static_inputs.json"


class BrokerConfig(BaseModel):
    broker_port: int = 23404
    broker_ip: str = "127.0.0.1"
    api_port: int = 12345
    feeder_host: str | None = None
    feeder_port: int | None = None


class HealthCheck(BaseModel):
    hostname: str
    host_ip: str


class HeathCheck(HealthCheck):
    """Deprecated: Use HealthCheck instead. This alias will be removed in a future version."""

    def __init__(self, **data):
        warnings.warn(
            "HeathCheck is deprecated and will be removed in a future version. "
            "Please use HealthCheck instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(**data)


class ServerReply(BaseModel):
    detail: str
    action: Optional[str] = None
