from data_types import *
from pydantic import BaseModel, Field, create_model
from typing import List, Optional


class StaticInputs(BaseModel):
    measurement_models: MeasurementModels


class DynamicInputs(BaseModel):
    admittance_matrix: AdmittanceMatrix
    regulator_steps: Optional[RegulatorSteps]
    switch_states: Optional[SwitchStates]
    capacitor_states: Optional[CapacitorStates]
    timeseries_values: TimeseriesValues


class DynamicOutputs(BaseModel):
    bus_voltage_values: BusVoltages
    bus_voltage_uncertanties: BusVoltages


class PNNLDistributedStateEstimation(BaseModel):
    Static_Inputs: StaticInputs
    Dynamic_Inputs: DynamicInputs
    Dynamic_Outputs: DynamicOutputs


print(PNNLDistributedStateEstimation.schema_json(indent=2))
