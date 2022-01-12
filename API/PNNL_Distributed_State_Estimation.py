from data_types import *
from pydantic import BaseModel, Field, create_model
from typing import List, Optional

class Static_Inputs(BaseModel):
    measurement_models: measurement_models_type

class Dynamic_Inputs(BaseModel):
    admittance_matrix: admittance_matrix_type
    regulator_steps: Optional[regulator_steps_type]
    switch_states: Optional[switch_states_type]
    capacitor_states: Optional[capacitor_states_type]
    timeseries_values: timeseries_values_type

class Dynamic_Outputs(BaseModel):
    bus_voltage_values: bus_voltages_type
    bus_voltage_uncertanties: bus_voltages_type


class PNNL_Distributed_State_Estimation(BaseModel):
    Static_Inputs: Static_Inputs
    Dynamic_Inputs: Dynamic_Inputs
    Dynamic_Outputs: Dynamic_Outputs

print(PNNL_Distributed_State_Estimation.schema_json(indent=2))

