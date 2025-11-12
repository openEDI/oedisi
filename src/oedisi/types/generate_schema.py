from .data_types import *
import os
import logging
import json

all_classes = [
    StateArray,
    SwitchStates,
    CapacitorStates,
    RegulatorStates,
    CostArray,
    RealCostFunctions,
    ReactiveCostFunctions,
    RealWholesalePrices,
    ReactiveWholesalePrices,
    OperationalCosts,
    MeasurementArray,
    VoltagesMagnitude,
    VoltagesAngle,
    VoltagesReal,
    VoltagesImaginary,
    CurrentsMagnitude,
    CurrentsAngle,
    CurrentsReal,
    CurrentsImaginary,
    PowersMagnitude,
    PowersAngle,
    PowersReal,
    PowersImaginary,
    PowersImaginary,
    SolarIrradiances,
    Temperatures,
    WindSpeeds,
    StatesOfCharge,
    Topology,
    AdmittanceSparse,
    AdmittanceMatrix,
    Injection,
    Command,
    CommandList,
    VVControl,
    VWControl,
    InverterControl,
    InverterControlList,
]

if not os.path.exists("schemas"):
    os.makedirs("schemas")

for klass in all_classes:
    logging.info(klass)
    with open(os.path.join("schemas", klass.__name__ + ".json"), "w") as fp:
        json.dump(klass.model_json_schema(), fp, indent=4)
