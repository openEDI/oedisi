import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import List

### Supporting Functions ###

class Complex(BaseModel):
    real: float
    imag: float

class Measurement_Type(str,Enum):
    voltage_magnitude='voltage_magnitude'
    voltage_angle = 'voltage_angle'
    current_magnitude = 'current_magnitude'
    current_angle = 'current_angle'

class Timeseries_Value(BaseModel):
    time: datetime.time
    value: float

class Measurement_Model(BaseModel):
    measurement_type: Measurement_Type = Field(None,alias='Measurement_Type')
    is_flow: bool
    standard_deviation: float

### Data Types ###

class admittance_matrix_type(BaseModel):
    data: List[List[Complex]]
    label: List[str]
    units: str = Field("Siemens")
    CIM_name: str = Field("")

class regulator_steps_type(BaseModel):
    data: List[int]
    label: List[str]
    units: None
    CIM_name: str = Field("")

class switch_states_type(BaseModel):
    data: List[bool]
    label: List[str]
    units: None
    CIM_name: str = Field("")

class capacitor_states_type(BaseModel):
    data: List[bool]
    label: List[str]
    units: None
    CIM_name: str = Field("")

class measurement_models_type(BaseModel):
    data: List[Measurement_Model]
    label: List[str]
    units: None
    CIM_name: str = Field("")

class timeseries_values_type(BaseModel):
    data: List[Timeseries_Value]
    label: List[str]
    units: None
    CIM_name: str = Field("")

class bus_voltages_type(BaseModel):
    data: List[Complex]
    label: List[str]
    units: str = Field("kV")
    CIM_name: str = Field("")

class line_flows_type(BaseModel):
    data: List[Complex]
    label: List[str]
    units: str = Field("Amps")
    CIM_name: str = Field("")

class power_data_type(BaseModel):
    data: List[Complex]
    label: List[str]
    units: str = Field("kVA")
    CIM_name: str = Field("")

class real_cost_functions_type(BaseModel):
    data: List[List[float]]
    label: List[str]
    units: str = Field("$/kWh")
    CIM_name: str = Field("")

class reactive_cost_functions_type(BaseModel):
    data: List[List[float]]
    label: List[str]
    units: str = Field("$/kVAh")
    CIM_name: str = Field("")

class operational_costs_type(BaseModel):
    data: List[float]
    label: List[str]
    units: str = Field("$")
    CIM_name: str = Field("")

class real_wholesale_prices_type(BaseModel):
    data: List[Timeseries_Value]
    label: List[str]
    units: str = Field("$/kWh")
    CIM_name: str = Field("")

class reactive_wholesale_prices_type(BaseModel):
    data: List[Timeseries_Value]
    label: List[str]
    units: str = Field("$/kVAh")
    CIM_name: str = Field("")

class state_of_charge_type(BaseModel):
    data: List[float]
    label: List[str]
    units: str = Field("Percent")
    CIM_name: str = Field("")


class path_type(BaseModel):
    data: str
    label: str
    units: str = None
    CIM_name: str = Field("")



#print(Matrix.schema_json(indent=2))
#print(Measurement_Model.schema_json(indent=2))
#test = Matrix(data=[[Complex(real=1,imag=2),Complex(real=2,imag=3)],[Complex(real=1,imag=2),Complex(real=4,imag=2)]],label=['a','b'])
#test2 = Measurement_Model( measurement_type = 'voltage_angle',is_flow =True,standard_deviation=0)
