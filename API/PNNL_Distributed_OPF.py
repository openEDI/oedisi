from data_types import *
from pydantic import BaseModel, Field, create_model
from typing import List, Optional

class Static_Inputs(BaseModel):
    pass

class Dynamic_Inputs(BaseModel):
    admittance_matrix: admittance_matrix_type
    regulator_steps: Optional[regulator_steps_type]
    switch_states: Optional[switch_states_type]
    capacitor_states: Optional[capacitor_states_type]
    generator_data: Optional[power_data_type]
    pv_data: Optional[power_data_type]
    storage_data: Optional[power_data_type]
    demand_data: power_data_type
    real_load_cost_functions: real_cost_functions_type
    reactive_load_cost_functions: reactive_cost_functions_type
    real_generator_cost_functions: Optional[real_cost_functions_type]
    reactive_generator_cost_functions: Optional[reactive_cost_functions_type]
    real_pv_cost_functions: Optional[real_cost_functions_type]
    reactive_pv_cost_functions: Optional[reactive_cost_functions_type]
    real_storage_cost_functions: Optional[real_cost_functions_type]
    reactive_storage_cost_functions: Optional[reactive_cost_functions_type]
    real_wholesale_prices: Optional[real_wholesale_prices_type]
    reactive_wholesale_prices: Optional[reactive_wholesale_prices_type]

class Dynamic_Outputs(BaseModel):
    bus_voltage_values: bus_voltages_type
    line_flows: line_flows_type
    pv_curtailment: Optional[power_data_type]
    load_curtailment: Optional[power_data_type]
    generator_setpoints: Optional[power_data_type]
    state_of_charge: Optional[state_of_charge_type]
    operational_cost: Optional[operational_costs_type]

class PNNL_Distributed_OPF(BaseModel):
    Static_Inputs: Static_Inputs
    Dynamic_Inputs: Dynamic_Inputs
    Dynamic_Outputs: Dynamic_Outputs

print(PNNL_Distributed_OPF.schema_json(indent=2))

#TODO: Add descriptions
#TODO (Later): Add Validation methods for certain criteria


