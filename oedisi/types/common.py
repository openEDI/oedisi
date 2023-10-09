from pydantic import BaseModel
from typing import Dict

APP_NAME = "oedisi"
class BrokerConfig(BaseModel):
    broker_port : int = 23404
    broker_ip : str = "10.5.0.2"
    api_port : int = 12345
    services : Dict = {}