import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import List,Optional

### Supporting Functions ###
# TODO: Connect with CIM values


class Complex(BaseModel):
    real: float
    imag: float

class StateArray(BaseModel):
    values: List[int]
    ids: List[str]
    state_type: StateType
    time: Optional[datetime.time]

class StateType(str, Enum):
    switch = "switch"
    capacitor = "capacitor"
    regulator = "regulator"

class CostArray(BaseModel):
    values: List[List[float]]
    ids: List[str]
    cost_type: CostType
    units: str
    time: Optional[datetime.time]

class CostType(BaseModel):
    real_cost_function: "real_cost_function"
    reactive_cost_function: "reactive_cost_function"
    real_wholesale_prices: "real_wholesale_prices"
    reactive_wholesale_prices: "reactive_wholesale_prices"
    operational_cost: "operational_cost"
    
class MeasurementArray(BaseModel):
    values: List[float]
    ids: List[str]
    units: str
    measurement_type: MeasurementType
    time: Optional[datetime.time]

class MeasurementType(str, Enum):
    voltage_magnitude = "voltage_magnitude"
    voltage_angle = "voltage_angle"
    voltage_real = "voltage_real"
    voltage_imaginary = "voltage_imaginary"
    current_magnitude = "current_magnitude"
    current_angle = "current_angle"
    current_real = "current_real"
    current_imaginary = "current_imaginary"
    power_magnitude = "power_magnitude"
    power_angle = "power_angle"
    power_imaginary = "power_imaginary"
    power_magnitude = "power_magnitude"
    state_of_charge = "state_of_charge"

class Topology(BaseModel):
    admittance_matrix: AdmittanceMatrix
    base_voltage_angles = MeasurementArray
    base_voltage_magnitudes = MeasurementArray
    slack_bus: str

class AdmittanceMatrix(BaseModel):
    values: List[List[Complex]]
    ids: List[str]
    units: str
