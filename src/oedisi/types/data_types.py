from __future__ import annotations
import datetime
from enum import Enum
from pydantic import BaseModel, root_validator
from typing import Tuple

### Supporting Functions ###
# TODO: Connect with CIM values


Complex = Tuple[float, float]


class StateArray(BaseModel):
    """
    Extended by classes:
        "SwitchStates",
        "CapacitorStates",
        "RegulatorStates".

    """

    values: list[int]
    ids: list[str]
    time: datetime.datetime | None


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
        "OperationalCosts".

    """

    values: list[list[float]]
    ids: list[str]
    units: str = "$"
    time: datetime.datetime | None


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
        "EquipmentNodeArray".
    """

    values: list[float]
    ids: list[str]
    units: str
    accuracy: list[float] | None
    bad_data_threshold: list[float] | None
    time: datetime.datetime | None


class BusArray(MeasurementArray):
    """
    Extended by classes:
        "VoltagesMagnitude",
        "VoltagesAngle",
        "VoltagesReal",
        "VoltagesImaginary".
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
        "ImpedanceImaginary".
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
        "PowersImaginary".

    """

    equipment_ids: list[str]


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
    admittance: AdmittanceSparse | AdmittanceMatrix
    injections: Injection
    incidences: IncidenceList | None = None
    base_voltage_angles: VoltagesAngle | None = None
    base_voltage_magnitudes: VoltagesMagnitude | None = None
    slack_bus: list[str] = []


class Incidence(BaseModel):
    from_equipment: list[str]
    to_equipment: list[str]
    equipment_type: list[str] | None


class IncidenceList(Incidence):
    ids: list[str]


class AdmittanceSparse(Incidence):
    admittance_list: list[Complex]
    units: str = "S"


class AdmittanceMatrix(BaseModel):
    admittance_matrix: list[list[Complex]]
    ids: list[str]
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
    val: int | float | str | list[int] | list[float] | list[str]


class CommandList(BaseModel):
    """List[Command] with JSON parsing."""

    __root__: list[Command]


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
    voltage: list[float]  # p.u. in V
    reactive_response: list[float]  # p.u. in VArs


class VWControl(BaseModel):
    """OpenDSS setting for volt-watt control."""

    deltap_factor: float = -1.0  # -1.0 tells OpenDSS to figure it out
    voltage: list[float]  # p.u. in V
    power_response: list[float]  # p.u. in VArs


class InverterControl(BaseModel):
    """InverterControl with volt-var control and/or volt-watt control."""

    pvsystem_list: list[str] | None = None
    vvcontrol: VVControl | None = None
    vwcontrol: VWControl | None = None
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

    __root__: list[InverterControl]
