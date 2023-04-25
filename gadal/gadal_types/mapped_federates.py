from enum import IntEnum, Enum

class AppPort(IntEnum):
    feeder =  8765
    measuring_federate = 8766

class AppIP(Enum):
    feeder =  '192.168.0.1'
    measuring_federate = '192.168.0.2'