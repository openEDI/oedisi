from data_types import *
from pydantic import BaseModel, Field, create_model
from typing import List, Optional

class Static_Inputs(BaseModel):
    opendss_model: path_type
    timeseries_folder: path_type

class Dynamic_Inputs(BaseModel):
    pass

class Dynamic_Outputs(BaseModel):
    bus_voltage_values: bus_voltages_type
    line_flows: line_flows_type
    admittance_matrix: admittance_matrix_type
    switch_states: switch_states_type
    capacitor_states: capacitor_states_type
    demand_data: power_data_type
    pv_data: power_data_type
    storage_data: power_data_type



class NREL_Powerflow_Simulation(BaseModel):
    Static_Inputs: Static_Inputs
    Dynamic_Inputs: Dynamic_Inputs
    Dynamic_Outputs: Dynamic_Outputs

print(NREL_Powerflow_Simulation.schema_json(indent=2))

