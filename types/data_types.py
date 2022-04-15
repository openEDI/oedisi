import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import List

### Supporting Functions ###


class Complex(BaseModel):
    real: float
    imag: float


class MeasurementType(str, Enum):
    voltage_magnitude = "voltage_magnitude"
    voltage_angle = "voltage_angle"
    current_magnitude = "current_magnitude"
    current_angle = "current_angle"


class TimeseriesValue(BaseModel):
    time: datetime.time
    value: float


class MeasurementModel(BaseModel):
    measurement_type: MeasurementType = Field(None, alias="Measurement_Type")
    is_flow: bool
    standard_deviation: float


class AdmittanceMatrix(BaseModel):
    "CIM_NAME:"
    data: List[List[Complex]]
    label: List[str]

    class Config:
        schema_extra = {"units": ""}


class RegulatorSteps(BaseModel):
    "CIM_NAME:"
    data: List[int]
    label: List[str]

    class Config:
        schema_extra = {"units": ""}


class SwitchStates(BaseModel):
    data: List[bool]
    label: List[str]


class CapacitorStates(BaseModel):
    data: List[bool]
    label: List[str]


class MeasurementModels(BaseModel):
    data: List[MeasurementModel]
    label: List[str]


class TimeseriesValues(BaseModel):
    data: List[TimeseriesValue]
    label: List[str]


class BusVoltages(BaseModel):
    data: List[Complex]
    label: List[str]

    class Config:
        schema_extra = {"units": "kV"}


class LineFlows(BaseModel):
    data: List[Complex]
    label: List[str]

    class Config:
        schema_extra = {"units": "Amps"}


class PowerData(BaseModel):
    data: List[Complex]
    label: List[str]

    class Config:
        schema_extra = {"units": "kVA"}


class RealCostFunctions(BaseModel):
    data: List[List[float]]
    label: List[str]

    class Config:
        schema_extra = {"units": "$/kWh"}


class ReactiveCostFunctions(BaseModel):
    data: List[List[float]]
    label: List[str]

    class Config:
        schema_extra = {"units": "$/kVarh"}


class OperationalCosts(BaseModel):
    data: List[float]
    label: List[str]

    class Config:
        schema_extra = {"units": "$"}


class RealWholesalePrices(BaseModel):
    data: List[TimeseriesValue]
    label: List[str]

    class Config:
        schema_extra = {"units": "$/kWh"}


class ReactiveWholesalePrices(BaseModel):
    data: List[TimeseriesValue]
    label: List[str]

    class Config:
        schema_extra = {"units": "$/kVarh"}


class StateOfCharge(BaseModel):
    data: List[float]
    label: List[str]

    class Config:
        schema_extra = {"units": "%"}


# print(Matrix.schema_json(indent=2))
# print(Measurement_Model.schema_json(indent=2))
# test = Matrix(data=[[Complex(real=1,imag=2),Complex(real=2,imag=3)],[Complex(real=1,imag=2),Complex(real=4,imag=2)]],label=['a','b'])
# test2 = Measurement_Model( measurement_type = 'voltage_angle',is_flow =True,standard_deviation=0)
