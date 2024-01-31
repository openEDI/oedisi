"""
Generate basic component from description JSON
"""

import json
import os
from shutil import copytree
from . import system_configuration
from .system_configuration import AnnotatedType
from pydantic import BaseModel
from typing import List, Any, Dict


class ComponentDescription(BaseModel):
    """Component description for simple ComponentType

    Parameters
    ----------
    directory :
        where code is stored relative to where this is run
    execute_function :
        command to execute component
    static_inputs :
        List of types for the parameter
    dynamic_inputs :
        List of input types. Typically subscriptions.
    dynamic_outputs :
        List of output types. Typically publications.
    """

    directory: str
    execute_function: str
    static_inputs: List[AnnotatedType]
    dynamic_inputs: List[AnnotatedType]
    dynamic_outputs: List[AnnotatedType]


def types_to_dict(types: List[AnnotatedType]):
    return {t.port_name: t for t in types}


def component_from_json(f, type_checker):
    comp_desc = ComponentDescription.parse_file(f)
    return basic_component(comp_desc, type_checker)


def basic_component(comp_desc: ComponentDescription, type_checker):
    """Uses data in component_definition to create a new component type

    Parameters
    ----------
    comp_desc : ComponentDescription
         Simplified component representation usually from a JSON file
    type_checker: function taking the type and value and returning a boolean

    Returns
    -------
    BasicComponent(system_configuration.ComponentType) :
         ComponentType from the description
    """

    class BasicComponent(system_configuration.ComponentType):
        _origin_directory = comp_desc.directory
        _execute_function = comp_desc.execute_function
        _dynamic_inputs = types_to_dict(comp_desc.dynamic_inputs)
        _dynamic_outputs = types_to_dict(comp_desc.dynamic_outputs)
        _static_inputs = types_to_dict(comp_desc.static_inputs)

        def __init__(
            self,
            name,
            parameters: Dict[str, Any],
            directory: str,
            host: str,
            port: int,
            comp_type: str,
        ):
            self._name = name
            self._directory = directory
            self._parameters = parameters
            self.check_parameters(parameters)
            self.copy_code_into_directory()
            self.generate_parameter_config()

        def check_parameters(self, parameters):
            for parameter_type in self._static_inputs.values():
                if parameter_type.port_name not in parameters:
                    return False
                if not type_checker(
                    parameter_type.type, parameters[parameter_type.port_name]
                ):
                    return False
            return True

        def copy_code_into_directory(self):
            copytree(self._origin_directory, self._directory, dirs_exist_ok=True)

        def generate_parameter_config(self):
            self._parameters["name"] = self._name
            with open(os.path.join(self._directory, "static_inputs.json"), "w") as f:
                json.dump(self._parameters, f)

        def generate_input_mapping(self, links):
            with open(os.path.join(self._directory, "input_mapping.json"), "w") as f:
                json.dump(links, f)

        @property
        def dynamic_inputs(self):
            return self._dynamic_inputs

        @property
        def dynamic_outputs(self):
            return self._dynamic_outputs

        @property
        def execute_function(self):
            return self._execute_function

    return BasicComponent
