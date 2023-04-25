from enum import IntEnum, Enum

class AppPort(IntEnum):
    feeder =  8765

class AppIP(Enum):
    feeder =  '192.168.0.1'