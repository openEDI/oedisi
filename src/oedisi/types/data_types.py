from __future__ import annotations
import datetime
from enum import Enum
from pydantic import BaseModel, root_validator
from typing import List, Optional, Union, Tuple

### Supporting Functions ###
# TODO: Connect with CIM values


Complex = Tuple[float, float]


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
    units: str = "$"
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
        "BusArray",
        "EquipmentArray",
        "EquipmentNodeArray"
    """

    values: List[float]
    ids: List[str]
    units: str
    accuracy: Optional[List[float]]
    bad_data_threshold: Optional[List[float]]
    time: Optional[datetime.datetime]


class BusArray(MeasurementArray):
    """
    Extended by classes:
        "VoltagesMagnitude",
        "VoltagesAngle",
        "VoltagesReal",
        "VoltagesImaginary"
    """

    pass


class EquipmentArray(MeasurementArray):
    """
    Extended by classes:
        "SolarIrradiances",
        "Temperatures",
        "WindSpeeds",
        "StatesOfCharge",
        "CurrentsMagnitude",
        "CurrentsAngle",
        "CurrentsReal",
        "CurrentsImaginary",
        "ImpedanceMagnitude",
        "ImpedanceAngle",
        "ImpedanceReal",
        "ImpedanceImaginary",
    """

    pass


class EquipmentNodeArray(MeasurementArray):
    """
    Primary key is ids + equipment_ids.

    - ids corresponding node id, so "113.1", "113.2", "113.3"
    - equipment_id corresponds to PVSystem.113

    Extended by classes:
        "PowersMagnitude",
        "PowersAngle",
        "PowersReal",
        "PowersImaginary",

    """

    equipment_ids: List[str]


class VoltagesMagnitude(BusArray):
    units: str = "kV"


class VoltagesAngle(BusArray):
    units: str = "degrees"


class VoltagesReal(BusArray):
    units: str = "kV"


class VoltagesImaginary(BusArray):
    units: str = "kV"


class CurrentsMagnitude(EquipmentArray):
    units: str = "A"


class CurrentsAngle(EquipmentArray):
    units: str = "degrees"


class CurrentsReal(EquipmentArray):
    units: str = "A"


class CurrentsImaginary(EquipmentArray):
    units: str = "A"


class ImpedanceReal(EquipmentArray):
    units: str = "Ohm"


class ImpedanceImaginary(EquipmentArray):
    units: str = "Ohm"


class ImpedanceMagnitude(EquipmentArray):
    units: str = "Ohm"


class ImpedanceAngle(EquipmentArray):
    units: str = "degrees"


class PowersMagnitude(EquipmentNodeArray):
    units: str = "kVA"


class PowersAngle(EquipmentNodeArray):
    units: str = "degrees"


class PowersReal(EquipmentNodeArray):
    units: str = "kW"


class PowersImaginary(EquipmentNodeArray):
    units: str = "kVAR"


class SolarIrradiances(EquipmentArray):
    units: str = "kW/m^2"


class Temperatures(EquipmentArray):
    units: str = "C"


class WindSpeeds(EquipmentArray):
    units: str = "m/s"


class StatesOfCharge(EquipmentArray):
    units: str = "percent"


class Topology(BaseModel):
    admittance: Union[AdmittanceSparse, AdmittanceMatrix]
    injections: Injection
    incidences: Optional[IncidenceList]
    base_voltage_angles: Optional[VoltagesAngle]
    base_voltage_magnitudes: Optional[VoltagesMagnitude]
    slack_bus: List[str] = []


class Incidence(BaseModel):
    from_equipment: List[str]
    to_equipment: List[str]
    equipment_type: Optional[List[str]]


class IncidenceList(Incidence):
    ids: List[str]


class AdmittanceSparse(Incidence):
    admittance_list: List[Complex]
    units: str = "S"


class AdmittanceMatrix(BaseModel):
    admittance_matrix: List[List[Complex]]
    ids: List[str]
    units: str = "S"


class Injection(BaseModel):
    # Shouldn't these be equipment arrays?
    current_real: CurrentsReal = {"values": [], "ids": [], "node_ids": []}
    current_imaginary: CurrentsImaginary = {"values": [], "ids": [], "node_ids": []}
    power_real: PowersReal = {"values": [], "ids": [], "node_ids": []}
    power_imaginary: PowersImaginary = {"values": [], "ids": [], "node_ids": []}
    impedance_real: ImpedanceReal = {"values": [], "ids": [], "node_ids": []}
    impedance_imaginary: ImpedanceImaginary = {"values": [], "ids": [], "node_ids": []}


Topology.update_forward_refs()


class Command(BaseModel):
    """JSON Configuration for external object commands.

    obj_name -- name of the object.
    obj_prop -- name of the property.
    obj_val -- val of the property.
    """

    obj_name: str
    obj_property: str
    val: Union[int, float, str, List[int], List[float], List[str]]


class CommandList(BaseModel):
    """List[Command] with JSON parsing."""

    __root__: List[Command]


class ReactivePowerSetting(Enum):
    """Reactive power setting, almost always VARAVAL_WATTS."""

    VARAVAL_WATTS = "VARAVAL_WATTS"
    VARMAX_VARS = "VARMAX_VARS"
    VARMAX_WATTS = "VARMAX_WATTS"


class InverterControlMode(Enum):
    """Inverter control mode."""

    voltvar = "VOLTVAR"
    voltwatt = "VOLTWATT"
    voltvar_voltwatt = "VV_VW"


class VVControl(BaseModel):
    """OpenDSS setting for volt-var control."""

    deltaq_factor: float = -1.0  # -1.0 tells OpenDSS to figure it out
    varchangetolerance: float = 0.025
    voltagechangetolerance: float = 0.0001
    vv_refreactivepower: ReactivePowerSetting = ReactivePowerSetting.VARAVAL_WATTS
    voltage: List[float]  # p.u. in V
    reactive_response: List[float]  # p.u. in VArs


class VWControl(BaseModel):
    """OpenDSS setting for volt-watt control."""

    deltap_factor: float = -1.0  # -1.0 tells OpenDSS to figure it out
    voltage: List[float]  # p.u. in V
    power_response: List[float]  # p.u. in VArs


class InverterControl(BaseModel):
    """InverterControl with volt-var control and/or volt-watt control."""

    pvsystem_list: Optional[List[str]] = None
    vvcontrol: Optional[VVControl] = None
    vwcontrol: Optional[VWControl] = None
    mode: InverterControlMode = InverterControlMode.voltvar

    @root_validator(pre=True)
    def check_mode(cls, values):
        """Make sure that mode reflects vvcontrol and vwcontrol data."""
        if "mode" not in values or (
            values["mode"] == InverterControlMode.voltvar
            or values["mode"] == InverterControlMode.voltvar_voltwatt
        ):
            assert "vvcontrol" in values and values["vvcontrol"] is not None
        if "mode" in values and (
            values["mode"] == InverterControlMode.voltwatt
            or values["mode"] == InverterControlMode.voltvar_voltwatt
        ):
            assert "vwcontrol" in values and values["vwcontrol"] is not None
        return values


class InverterControlList(BaseModel):
    """List[InverterControl] with JSON parsing."""

    __root__: List[InverterControl]
