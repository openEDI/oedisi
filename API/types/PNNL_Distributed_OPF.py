from data_types import *
from pydantic import BaseModel, Field, create_model
from typing import List, Optional

class StaticInputs(BaseModel):
    pass

class DynamicInputs(BaseModel):
    admittance_matrix: AdmittanceMatrix
    regulator_steps: Optional[RegulatorSteps]
    switch_states: Optional[SwitchStates]
    capacitor_states: Optional[CapacitorStates]
    generator_data: Optional[PowerData]
    pv_data: Optional[PowerData]
    storage_data: Optional[PowerData]
    demand_data: PowerData
    real_load_cost_functions: RealCostFunctions
    reactive_load_cost_functions: ReactiveCostFunctions
    real_generator_cost_functions: Optional[RealCostFunctions]
    reactive_generator_cost_functions: Optional[ReactiveCostFunctions]
    real_pv_cost_functions: Optional[RealCostFunctions]
    reactive_pv_cost_functions: Optional[ReactiveCostFunctions]
    real_storage_cost_functions: Optional[RealCostFunctions]
    reactive_storage_cost_functions: Optional[ReactiveCostFunctions]
    real_wholesale_prices: Optional[RealWholesalePrices]
    reactive_wholesale_prices: Optional[ReactiveWholesalePrices]

class DynamicOutputs(BaseModel):
    bus_voltage_values: BusVoltages
    line_flows: LineFlows
    pv_curtailment: Optional[PowerData]
    load_curtailment: Optional[PowerData]
    generator_setpoints: Optional[PowerData]
    state_of_charge: Optional[StateOfCharge]
    operational_cost: Optional[OperationalCosts]

class PNNLDistributedOPF(BaseModel):
    static_inputs: StaticInputs
    dynamic_inputs: DynamicInputs
    dynamic_outputs: DynamicOutputs

print(PNNLDistributedOPF.schema_json(indent=2))

#TODO: Add descriptions
#TODO (Later): Add Validation methods for certain criteria


