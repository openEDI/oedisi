"""Common types and constants for OEDISI components."""

from pydantic import BaseModel
from enum import Enum
import warnings

BASE_DOCKER_IMAGE = "python:3.10.6-slim-bullseye"
BROKER_SERVICE = "broker"
APP_NAME = "oedisi"
DOCKER_HUB_USER = "aadillatif"
KUBERNETES_SERVICE_PREFIX = "svc"


class DefaultFileNames(str, Enum):
    """Standard filenames for component configuration files.

    `oedisi build` will create an input_mapping.json and static_inputs.json
    with the appropriate configuration.
    """

    INPUT_MAPPING = "input_mapping.json"
    "File path for dictionary of 'input port' name to the HELICS subscription key."
    STATIC_INPUTS = "static_inputs.json"
    "File path for configuration of the component."


class BrokerConfig(BaseModel):
    """Configuration for HELICS broker connection.

    Used for transmitting broker location to Kubernetes federates.
    """

    broker_port: int = 23404
    "Port for HELICS broker"
    broker_ip: str = "127.0.0.1"
    "IP for HELICS broker"
    api_port: int = 12345
    "REST API of the HELICS broker"
    feeder_host: str | None = None
    "IP for the feeder federate (may not exist or be unique)"
    feeder_port: int | None = None
    "Port for the feeder federate (may not exist or be unique)"


class HealthCheck(BaseModel):
    """Health check response for component status."""

    hostname: str
    "Current hostname known to the component"
    host_ip: str
    "Current IP known to the component"


class HeathCheck(HealthCheck):
    """Deprecated: Use HealthCheck instead.

    This alias will be removed in a future version.
    """

    def __init__(self, **data):
        warnings.warn(
            "HeathCheck is deprecated and will be removed in a future version. "
            "Please use HealthCheck instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(**data)


class ServerReply(BaseModel):
    """Standard server response message."""

    detail: str
    "Human readable text response."
    action: str | None = None
    "Specific action taken. Should almost always be None."
