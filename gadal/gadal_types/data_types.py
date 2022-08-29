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
    equipment_type: Optional[List[str]]
    accuracy: Optional[List[float]]
    bad_data_threshold: Optional[List[float]]
    time: Optional[datetime.datetime]

class VoltagesMagnitude(MeasurementArray):
    units: str = 'kV'

class VoltagesAngle(MeasurementArray):
    units: str = 'degrees'

class VoltagesReal(MeasurementArray):
    units: str = 'kV'

class VoltagesImaginary(MeasurementArray):
    units: str = 'kV'

class CurrentsMagnitude(MeasurementArray):
    units: str = 'A'

class CurrentsAngle(MeasurementArray):
    units: str = 'degrees'

class CurrentsReal(MeasurementArray):
    units: str = 'A'

class CurrentsImaginary(MeasurementArray):
    units: str = 'A'

class ImpedanceReal(MeasurementArray):
    units: str = 'Ohm'

class ImpedanceImaginary(MeasurementArray):
    units: str = 'Ohm'

class ImpedanceMagnitude(MeasurementArray):
    units: str = 'Ohm'

class ImpedanceAngle(MeasurementArray):
    units: str = 'degrees'

class PowersMagnitude(MeasurementArray):
    units: str = 'kVA'

class PowersAngle(MeasurementArray):
    units: str = 'degrees'

class PowersReal(MeasurementArray):
    units: str = 'kW'

class PowersImaginary(MeasurementArray):
    units: str = 'kVAR'

class SolarIrradiances(MeasurementArray):
    units: str = 'W/m^2'

class Temperatures(MeasurementArray):
    units: str = 'C'

class WindSpeeds(MeasurementArray):
    units: str = 'm/s'

class StatesOfCharge(MeasurementArray):
    units: str = 'percent'


class Topology(BaseModel):
    admittance:  Union[AdmittanceSparse, AdmittanceMatrix]
    injections: Injection
    incidences: Optional[Incidence]
    base_voltage_angles: Optional[VoltagesAngle]
    base_voltage_magnitudes: Optional[VoltagesMagnitude]
    slack_bus: List[str] = []

class Incidence(BaseModel):
    from_equipment: List[str]    
    to_equipment:    List[str]    
    equipment_type: Optional[List[str]]

class AdmittanceSparse(Incidence):
    admittance_list: List[Complex]
    units:  str = 'S'

class AdmittanceMatrix(BaseModel):
    admittance_matrix: List[List[Complex]]
    ids: List[str]
    units: str = 'S'

class Injection(BaseModel):
    current_real: CurrentsReal = {"values":[], "ids":[]}
    current_imaginary: CurrentsImaginary = {"values":[], "ids":[]}
    power_real: PowersReal = {"values":[], "ids":[]}
    power_imaginary: PowersImaginary = {"values":[], "ids":[]}
    impedance_real: ImpedanceReal = {"values":[], "ids":[]}
    impedance_imaginary: ImpedanceImaginary = {"values":[], "ids":[]}

Topology.update_forward_refs()
