from pydantic import BaseModel


class BrokerConfig(BaseModel):
    broker_port : int = 23405
    broker_ip : str = "10.5.0.2"