from __future__ import annotations
import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Tuple

### Supporting Functions ###
# TODO: Connect with CIM values


Complex = Tuple[float,float]

class StateArray(BaseModel):
    """
    Extended by classes:
        "SwitchStates",
        "CapacitorStates",
        "RegulatorStates"

    """
    values: List[int]
    ids: List[str]
    time: Optional[datetime.datetime]

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
    units: str = '$'
    time: Optional[datetime.datetime]

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
    accuracy: Optional[List[float]]
    bad_data_threshold: Optional[List[float]]
    time: Optional[datetime.datetime]

class VoltagesMagnitude(MeasurementArray):
    units: str = 'kV'
    pass

class VoltagesAngle(MeasurementArray):
    units: str = 'degrees'
    pass

class VoltagesReal(MeasurementArray):
    units: str = 'kV'
    pass

class VoltagesImaginary(MeasurementArray):
    units: str = 'kV'
    pass

class CurrentsMagnitude(MeasurementArray):
    units: str = 'A'
    pass

class CurrentsAngle(MeasurementArray):
    units: str = 'degrees'
    pass

class CurrentsReal(MeasurementArray):
    units: str = 'A'
    pass

class CurrentsImaginary(MeasurementArray):
    units: str = 'A'
    pass

class PowersMagnitude(MeasurementArray):
    injection: List[bool]
    units: str = 'kVA'
    pass

class PowersAngle(MeasurementArray):
    injection: List[bool]
    units: str = 'degrees'
    pass

class PowersReal(MeasurementArray):
    injection: List[bool]
    units: str = 'kW'
    pass

class PowersImaginary(MeasurementArray):
    injection: List[bool]
    units: str = 'kVAR'
    pass

class SolarIrradiances(MeasurementArray):
    units: str = 'W/m^2'
    pass

class Temperatures(MeasurementArray):
    units: str = 'C'
    pass

class WindSpeeds(MeasurementArray):
    units: str = 'm/s'
    pass

class StatesOfCharge(MeasurementArray):
    units: str = 'percent'
    pass


class Topology(BaseModel):
    admittance:  Union[AdmittanceSparse, AdmittanceMatrix]
    base_voltage_angles: Optional[VoltagesAngle]
    base_voltage_magnitudes: Optional[VoltagesMagnitude]
    slack_bus: List[str] = []


class AdmittanceSparse(BaseModel):
    admittance_list: List[Complex]
    from_equipment: List[str]    
    to_equipment:    List[str]    
    equipment_type: Optional[List[str]]
    units = str = 'S'

class AdmittanceMatrix(BaseModel):
    admittance_matrix: List[List[Complex]]
    ids: List[str]
    units: str = 'S'

Topology.update_forward_refs()
