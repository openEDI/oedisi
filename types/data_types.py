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
    time: Optional[datetime.time]
    allowed_types = [
        "SwitchStates",
        "CapacitorStates",
        "RegulatorStates"
    ]
class SwitchStates(StateArray):
    pass

class CapacitorStates(StateArray):
    pass

class RegulatorStates(StateArray):
    pass

class CostArray(BaseModel):
    values: List[List[float]]
    ids: List[str]
    units: str
    time: Optional[datetime.time]
    allowed_types = [
        "RealCostFunctions",
        "ReactiveCostFunctions",
        "RealWholesalePrices",
        "ReactiveWholesalePrices",
        "OperationalCosts"
    ]

class RealCostFunctions(CostArray):
    pass

class ReactiveCostFunctions(CostArray):
    pass

class RealWholesalePrices(CostArray):
    pass

class ReactiveWholesalePrices(CostArray):
    pass

class OperationalCosts(CostArray):
    pass

class MeasurementArray(BaseModel):
    values: List[float]
    ids: List[str]
    units: str
    time: Optional[datetime.time]
    allowed_types = [
        "VoltagesMagnitude",
        "VoltagesAngle",
        "VoltagesReal",
        "VoltagesImaginary",
        "CurrentsMagnitude",
        "CurrentsAngle",
        "CurrentsReal",
        "CurrentsImaginary",
        "PowersMagnitude",
        "PowersAngle",
        "PowersReal",
        "PowersImaginary",
        "StatesOfCharge"
    ]

class VoltagesMagnitude(MeasurementArray):
    pass

class VoltagesAngle(MeasurementArray):
    pass

class VoltagesReal(MeasurementArray):
    pass

class VoltagesImaginary(MeasurementArray):
    pass

class CurrentsMagnitude(MeasurementArray):
    pass

class CurrentsAngle(MeasurementArray):
    pass

class CurrentsReal(MeasurementArray):
    pass

class CurrentsImaginary(MeasurementArray):
    pass

class PowersMagnitude(MeasurementArray):
    pass

class PowersAngle(MeasurementArray):
    pass

class PowersReal(MeasurementArray):
    pass

class PowersImaginary(MeasurementArray):
    pass

class StatesOfCharge(MeasurementArray):
    pass


class Topology(BaseModel):
    admittance_matrix: AdmittanceMatrix
    base_voltage_angles = VoltagesAngle
    base_voltage_magnitudes = VoltagesMagnitude
    slack_bus: str

class AdmittanceMatrix(BaseModel):
    values: List[List[Complex]]
    ids: List[str]
    units: str
