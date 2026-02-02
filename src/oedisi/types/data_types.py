"""Power system data types for OEDISI measurements and control."""

from __future__ import annotations
import datetime
from enum import Enum
from pydantic import model_validator, BaseModel, RootModel, Field

### Supporting Functions ###

Complex = tuple[float, float]


class StateArray(BaseModel):
    """Base class for power system equipment state arrays.

    Extended by classes:
        "SwitchStates",
        "CapacitorStates",
        "RegulatorStates".

    """

    values: list[int]
    ids: list[str]
    time: datetime.datetime | None = None


class SwitchStates(StateArray):
    """Switch state data for power system equipment."""

    pass


class CapacitorStates(StateArray):
    """Capacitor state data for power system equipment."""

    pass


class RegulatorStates(StateArray):
    """Voltage regulator state data for power system equipment."""

    pass


class CostArray(BaseModel):
    """Base class for cost-related data arrays.

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
    time: datetime.datetime | None = None


class RealCostFunctions(CostArray):
    """Real power cost functions for equipment."""

    pass


class ReactiveCostFunctions(CostArray):
    """Reactive power cost functions for equipment."""

    pass


class RealWholesalePrices(CostArray):
    """Real power wholesale price data for equipment."""

    pass


class ReactiveWholesalePrices(CostArray):
    """Reactive power wholesale price data for equipment."""

    pass


class OperationalCosts(CostArray):
    """Operational cost data for equipment."""

    pass


class MeasurementArray(BaseModel):
    """Base class for measurement data arrays.

    Extended by classes:
        "BusArray",
        "EquipmentArray",
        "EquipmentNodeArray".
    """

    values: list[float]
    ids: list[str]
    units: str
    accuracy: list[float] | None = None
    bad_data_threshold: list[float] | None = None
    time: datetime.datetime | None = None


class BusArray(MeasurementArray):
    """Measurements for or at power system buses (primarily voltages)."""

    pass


class EquipmentArray(MeasurementArray):
    """Measurements at equipment nodes (currents, impedances, environmental)."""

    pass


class EquipmentNodeArray(MeasurementArray):
    """Power measurements at equipment nodes (primary key: ids + equipment_ids).

    Primary key is ids + equipment_ids where ids correspond to node ids
    (e.g., "113.1", "113.2", "113.3") and equipment_ids correspond to
    equipment identifiers (e.g., PVSystem.113).
    """

    equipment_ids: list[str]


class VoltagesMagnitude(BusArray):
    """Voltage magnitude measurements at buses."""

    units: str = "V"


class VoltagesAngle(BusArray):
    """Voltage angle measurements at buses."""

    units: str = "radians"


class VoltagesReal(BusArray):
    """Real component of voltage measurements at buses."""

    units: str = "V"


class VoltagesImaginary(BusArray):
    """Imaginary component of voltage measurements at buses."""

    units: str = "V"


class CurrentsMagnitude(EquipmentArray):
    """Current magnitude measurements at equipment."""

    units: str = "A"


class CurrentsAngle(EquipmentArray):
    """Current angle measurements at equipment."""

    units: str = "radians"


class CurrentsReal(EquipmentArray):
    """Real component of current measurements at equipment."""

    units: str = "A"


class CurrentsImaginary(EquipmentArray):
    """Imaginary component of current measurements at equipment."""

    units: str = "A"


class ImpedanceReal(EquipmentArray):
    """Real component of impedance measurements at equipment."""

    units: str = "Ohm"


class ImpedanceImaginary(EquipmentArray):
    """Imaginary component of impedance measurements at equipment."""

    units: str = "Ohm"


class ImpedanceMagnitude(EquipmentArray):
    """Impedance magnitude measurements at equipment."""

    units: str = "Ohm"


class ImpedanceAngle(EquipmentArray):
    """Impedance angle measurements at equipment."""

    units: str = "radians"


class PowersMagnitude(EquipmentNodeArray):
    """Power magnitude (apparent power) measurements at equipment nodes."""

    units: str = "kVA"


class PowersAngle(EquipmentNodeArray):
    """Power angle measurements at equipment nodes."""

    units: str = "radians"


class PowersReal(EquipmentNodeArray):
    """Real power measurements at equipment nodes."""

    units: str = "kW"


class PowersImaginary(EquipmentNodeArray):
    """Reactive power measurements at equipment nodes."""

    units: str = "kVAR"


class SolarIrradiances(EquipmentArray):
    """Solar irradiance measurements at equipment."""

    units: str = "kW/m^2"


class Temperatures(EquipmentArray):
    """Temperature measurements at equipment."""

    units: str = "C"


class WindSpeeds(EquipmentArray):
    """Wind speed measurements at equipment."""

    units: str = "m/s"


class StatesOfCharge(EquipmentArray):
    """State of charge measurements for energy storage equipment."""

    units: str = "percent"


class Topology(BaseModel):
    """Power system network topology with admittance and injection data."""

    admittance: AdmittanceSparse | AdmittanceMatrix
    injections: Injection
    incidences: IncidenceList | None = None
    base_voltage_angles: VoltagesAngle | None = None
    base_voltage_magnitudes: VoltagesMagnitude | None = None
    slack_bus: list[str] = []


class Incidence(BaseModel):
    """Incidence relationships between equipment in the power system."""

    from_equipment: list[str]
    to_equipment: list[str]
    equipment_type: list[str] | None = None


class IncidenceList(Incidence):
    """Incidence relationships with associated identifiers."""

    ids: list[str]


class AdmittanceSparse(Incidence):
    """Sparse representation of network admittance matrix."""

    admittance_list: list[Complex]
    units: str = "S"


class AdmittanceMatrix(BaseModel):
    """Dense representation of network admittance matrix."""

    admittance_matrix: list[list[Complex]]
    ids: list[str]
    units: str = "S"


class Injection(BaseModel):
    """Current and power injections at network nodes."""

    # Shouldn't these be equipment arrays?
    current_real: CurrentsReal = Field(
        default_factory=lambda: CurrentsReal(values=[], ids=[], units="A")
    )
    current_imaginary: CurrentsImaginary = Field(
        default_factory=lambda: CurrentsImaginary(values=[], ids=[], units="A")
    )
    power_real: PowersReal = Field(
        default_factory=lambda: PowersReal(values=[], ids=[], equipment_ids=[], units="kW")
    )
    power_imaginary: PowersImaginary = Field(
        default_factory=lambda: PowersImaginary(
            values=[], ids=[], equipment_ids=[], units="kVAR"
        )
    )
    impedance_real: ImpedanceReal = Field(
        default_factory=lambda: ImpedanceReal(values=[], ids=[], units="Ohm")
    )
    impedance_imaginary: ImpedanceImaginary = Field(
        default_factory=lambda: ImpedanceImaginary(values=[], ids=[], units="Ohm")
    )


class Command(BaseModel):
    """JSON Configuration for external object commands.

    obj_name -- name of the object.
    obj_prop -- name of the property.
    obj_val -- val of the property.
    """

    obj_name: str
    obj_property: str
    val: str


CommandList = RootModel[list[Command]]


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

    @model_validator(mode="before")
    @classmethod
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


InverterControlList = RootModel[list[InverterControl]]
