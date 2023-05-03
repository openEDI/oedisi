from enum import IntEnum, Enum

class AppPort(IntEnum):
    feeder =  8765
    measuring_federate = 8766
    wls_federate = 8767
    recorder = 8768
    broker = 8769

class AppIP(Enum):
    feeder =  '192.168.0.1'
    measuring_federate = '192.168.0.2'
    wls_federate = '192.168.0.3'
    recorder = '192.168.0.4'
    broker = '192.168.0.5'