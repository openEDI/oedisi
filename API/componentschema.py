from pydantic import BaseModel
from typing import List, Optional
from devtools import debug

class AnnotatedType(BaseModel):
    "Class for representing types"
    type: str
    description: Optional[str]
    unit: Optional[str]
    port_id: Optional[str]

    @property
    def port_id(self):
        if self.port_id is None:
            return self.type
        return self.port_id


class ComponentDescription(BaseModel):
    directory: str
    execution_function: str
    static_inputs: List[AnnotatedType]
    dynamic_inputs: List[AnnotatedType]
    dynamic_outputs: List[AnnotatedType]


static_inputs = [
    AnnotatedType(type='Path', port_id='opendss_model'),
]
dynamic_inputs = []
dynamic_outputs = [
    AnnotatedType(type='SwitchStates')
]

test_component = ComponentDescription(
    directory='',
    execution_function='',
    static_inputs=static_inputs,
    dynamic_inputs=dynamic_inputs,
    dynamic_outputs=dynamic_outputs
)
debug(test_component)
