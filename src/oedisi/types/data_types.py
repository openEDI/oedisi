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
    "List of values"
    ids: list[str]
    "List of ids which values applies to"
    time: datetime.datetime | None = None
    "Time of original measurement"


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
    "List of cost arrays"
    ids: list[str]
    "List of ids which values applies to"
    units: str = "$"
    "Cost unit of float"
    time: datetime.datetime | None = None
    "Time of measurement"


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
    "List of values"
    ids: list[str]
    "List of ids which values applies to"
    units: str
    "Unit of each float"
    accuracy: list[float] | None = None
    "Estimated or known std error at each location"
    bad_data_threshold: list[float] | None = None
    "Threshold after which value should be considered junk"
    time: datetime.datetime | None = None
    "Time of original measurement"


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
    "Unique ID for values such as 'PVSystem.113'"


class VoltagesMagnitude(BusArray):
    """Voltage magnitude measurements at buses."""

    units: str = "V"
    "Unit for voltage"


class VoltagesAngle(BusArray):
    """Voltage angle measurements at buses."""

    units: str = "radians"
    "Unit for angle"


class VoltagesReal(BusArray):
    """Real component of voltage measurements at buses."""

    units: str = "V"
    "Unit for voltage"


class VoltagesImaginary(BusArray):
    """Imaginary component of voltage measurements at buses."""

    units: str = "V"
    "Unit for voltage"


class CurrentsMagnitude(EquipmentArray):
    """Current magnitude measurements at equipment."""

    units: str = "A"
    "Unit for current"


class CurrentsAngle(EquipmentArray):
    """Current angle measurements at equipment."""

    units: str = "radians"
    "Unit for angle"


class CurrentsReal(EquipmentArray):
    """Real component of current measurements at equipment."""

    units: str = "A"
    "Unit for current"


class CurrentsImaginary(EquipmentArray):
    """Imaginary component of current measurements at equipment."""

    units: str = "A"
    "Unit for current"


class ImpedanceReal(EquipmentArray):
    """Real component of impedance measurements at equipment."""

    units: str = "Ohm"
    "Unit for impedance"


class ImpedanceImaginary(EquipmentArray):
    """Imaginary component of impedance measurements at equipment."""

    units: str = "Ohm"
    "Unit for impedance"


class ImpedanceMagnitude(EquipmentArray):
    """Impedance magnitude measurements at equipment."""

    units: str = "Ohm"
    "Unit for impedance"


class ImpedanceAngle(EquipmentArray):
    """Impedance angle measurements at equipment."""

    units: str = "radians"
    "Unit for angle"


class PowersMagnitude(EquipmentNodeArray):
    """Power magnitude (apparent power) measurements at equipment nodes."""

    units: str = "kVA"
    "Unit for power"


class PowersAngle(EquipmentNodeArray):
    """Power angle measurements at equipment nodes."""

    units: str = "radians"
    "Unit for angle"


class PowersReal(EquipmentNodeArray):
    """Real power measurements at equipment nodes."""

    units: str = "kW"
    "Unit for power"


class PowersImaginary(EquipmentNodeArray):
    """Reactive power measurements at equipment nodes."""

    units: str = "kVAR"
    "Unit for power"


class SolarIrradiances(EquipmentArray):
    """Solar irradiance measurements at equipment."""

    units: str = "kW/m^2"
    "Unit for power per area"


class Temperatures(EquipmentArray):
    """Temperature measurements at equipment."""

    units: str = "C"
    "Unit for temperature"


class WindSpeeds(EquipmentArray):
    """Wind speed measurements at equipment."""

    units: str = "m/s"
    "Unit for speed"


class StatesOfCharge(EquipmentArray):
    """State of charge measurements for energy storage equipment."""

    units: str = "percent"
    "Dimensionless unit"


class Topology(BaseModel):
    """Power system network topology with admittance and injection data."""

    admittance: AdmittanceSparse | AdmittanceMatrix
    "Admittance matrix either as AdmittanceSparse or AdmittanceMatrix"
    injections: Injection
    "Base injections for all equipment"
    incidences: IncidenceList | None = None
    "Connectivity of all equipment"
    base_voltage_angles: VoltagesAngle | None = None
    "Base voltage angles at each bus"
    base_voltage_magnitudes: VoltagesMagnitude | None = None
    "Base voltage mangitudes at each bus"
    slack_bus: list[str] = []
    "Slack bus (usually 3 buses for each phase)"


class Incidence(BaseModel):
    """Incidence relationships between equipment in the power system.

    Each list should have the same length. 3W transformers are transformed
    into 2 separate edges.
    """

    from_equipment: list[str]
    "For connection i, from_equpiment[i] is the source bus."
    to_equipment: list[str]
    "For connection i, to_equipment[i] is the source bus."
    equipment_type: list[str] | None = None
    "For connection i, equipment_type[i] is the target bus."


class IncidenceList(Incidence):
    """Incidence relationships with associated identifiers."""

    ids: list[str]
    "String ID for each connection such as branch ID"


class AdmittanceSparse(Incidence):
    """Sparse representation of network admittance matrix."""

    admittance_list: list[Complex]
    "Sparse admittance values with incidence connections"
    units: str = "S"
    "Unit for admittance"


class AdmittanceMatrix(BaseModel):
    """Dense representation of network admittance matrix."""

    admittance_matrix: list[list[Complex]]
    "Dense matrix for admittance"
    ids: list[str]
    "Row and column bus IDs"
    units: str = "S"
    "Unit for admittance"


class Injection(BaseModel):
    """Current and power injections at network nodes."""

    # Shouldn't these be equipment arrays?
    current_real: CurrentsReal = Field(
        default_factory=lambda: CurrentsReal(values=[], ids=[], units="A"),
        description="Fixed real current injections",
    )
    current_imaginary: CurrentsImaginary = Field(
        default_factory=lambda: CurrentsImaginary(values=[], ids=[], units="A"),
        description="Fixed imaginary current injections",
    )
    power_real: PowersReal = Field(
        default_factory=lambda: PowersReal(values=[], ids=[], equipment_ids=[], units="kW"),
        description="Fixed real power injections",
    )
    power_imaginary: PowersImaginary = Field(
        default_factory=lambda: PowersImaginary(
            values=[], ids=[], equipment_ids=[], units="kVAR"
        ),
        description="Fixed imaginary power injections",
    )
    impedance_real: ImpedanceReal = Field(
        default_factory=lambda: ImpedanceReal(values=[], ids=[], units="Ohm"),
        description="Fixed real impedances",
    )
    impedance_imaginary: ImpedanceImaginary = Field(
        default_factory=lambda: ImpedanceImaginary(values=[], ids=[], units="Ohm"),
        description="Fixed imaginary impedances",
    )


class Command(BaseModel):
    """JSON Configuration for external object commands for OpenDSS."""

    obj_name: str
    "Name of OpenDSS object to change"
    obj_property: str
    "Property of OpenDSS object to change"
    val: str
    "New value. All OpenDSS transfers must be str"


CommandList = RootModel[list[Command]]


class ReactivePowerSetting(Enum):
    """Reactive power setting, almost always VARAVAL_WATTS.

    See https://dss-extensions.org/dss-format/InvControl.html.
    """

    VARAVAL_WATTS = "VARAVAL_WATTS"
    "Base absorbed reactive power is equal to available"
    VARMAX_VARS = "VARMAX_VARS"
    "Base absorbed reactive power equal to kvar maximum"
    VARMAX_WATTS = "VARMAX_WATTS"
    "Base absorbed reactive power equal to power magnitude maximum"


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
    """OpenDSS setting for volt-watt control.

    See https://dss-extensions.org/dss-format/InvControl.html.
    """

    deltap_factor: float = -1.0  # -1.0 tells OpenDSS to figure it out
    """DeltaP_factor used to limit change for control iterations.

    By default uses OpenDSS to figure it out."""
    voltage: list[float]
    "Voltage response coordinates (V)"
    power_response: list[float]
    "Power response coordinates (p.u. of VAs)"


class InverterControl(BaseModel):
    """InverterControl with volt-var control and/or volt-watt control.

    See https://dss-extensions.org/dss-format/InvControl.html.
    """

    pvsystem_list: list[str] | None = None
    "List of pvsystems to apply controls to"
    vvcontrol: VVControl | None = None
    "Volt-var control settings"
    vwcontrol: VWControl | None = None
    "Volt-watt control settings"
    mode: InverterControlMode = InverterControlMode.voltvar
    "Inverter control mode"

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
