from data_types import *
from pydantic import BaseModel, Field, create_model
from typing import List, Optional
from pathlib import Path


class StaticInputs(BaseModel):
    opendss_model: Path
    timeseries_folder: Path


class DynamicInputs(BaseModel):
    pass


class DynamicOutputs(BaseModel):
    bus_voltage_values: BusVoltages
    line_flows: LineFlows
    admittance_matrix: AdmittanceMatrix
    switch_states: SwitchStates
    capacitor_states: CapacitorStates
    demand_data: PowerData
    pv_data: PowerData
    storage_data: PowerData


class NRELPowerflowSimulation(BaseModel):
    StaticInputs: StaticInputs
    DynamicInputs: DynamicInputs
    DynamicOutputs: DynamicOutputs


print(NRELPowerflowSimulation.schema_json(indent=2))
