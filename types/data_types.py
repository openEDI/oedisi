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
    """
    Extended by classes:
        "SwitchStates",
        "CapacitorStates",
        "RegulatorStates"

    """
    values: List[int]
    ids: List[str]
    time: Optional[datetime.time]

class SwitchStates(StateArray):
    pass

class CapacitorStates(StateArray):
    pass

class RegulatorStates(StateArray):
    pass

class CostArray(BaseModel):
    """
    Extended by classes:
        "RealCostFunctions",
        "ReactiveCostFunctions",
        "RealWholesalePrices",
        "ReactiveWholesalePrices",
        "OperationalCosts"

    """
    values: List[List[float]]
    ids: List[str]
    units: str
    time: Optional[datetime.time]

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
    """
    Extended by classes:
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
        "SolarIrradiances",
        "Temperatures",
        "WindSpeeds",
        "StatesOfCharge"

    """
    values: List[float]
    ids: List[str]
    units: str
    injection: Optional[List[bool]]
    accuracy: Optional[List[float]]
    bad_data_threshold: Optional[List[float]]
    time: Optional[datetime.time]

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

class SolarIrradiances(MeasurementArray):
    pass

class Temperatures(MeasurementArray):
    pass

class WindSpeeds(MeasurementArray):
    pass

class StatesOfCharge(MeasurementArray):
    pass


class Topology(BaseModel):
    admittance:  Union[AdmittanceSparse, AdmittanceMatrix]
    base_voltage_angles = Optional[VoltagesAngle]
    base_voltage_magnitudes = Optional[VoltagesMagnitude]
    slack_bus: List[str]

class AdmittanceSparse(BaseModel):
    admittance_list: List[Complex]
    from_equipment: List[str]    
    to_equipment:    List[str]    
    equipment_type: Optional[List[str]]
    units = str

class AdmittanceMatrix(BaseModel):
    admittance_matrix: List[List[Complex]]
    ids: List[str]
    units: str
