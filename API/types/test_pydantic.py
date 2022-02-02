#!/usr/bin/env python3

from typing import Generic, TypeVar, Optional, List, Literal

from pydantic import BaseModel, validator, ValidationError
from pydantic.generics import GenericModel

Unit = TypeVar('Unit')

class Complex(BaseModel):
    real: float
    imag: float


class AdmittanceMatrix(BaseModel):
    "CIM_NAME: "
    data: List[List[Complex]]
    label: List[str]

    class Config:
        schema_extra = {
            'unit': 'm/s',
        }

print(AdmittanceMatrix.schema_json(indent=2))
