"""Generate basic component from description JSON."""

import json
import os
from shutil import copytree
from typing import Any

from pydantic import BaseModel, Field

from . import system_configuration
from .system_configuration import AnnotatedType
from oedisi.types.helics_config import HELICSFederateConfig


class ComponentCapabilities(BaseModel):
    """Component capability declarations for build-time validation.

    Parameters
    ----------
    version :
        Capabilities schema version.
    broker_config :
        Whether this component supports receiving federate_config in static_inputs.json.
        If True, the component can be used with WiringDiagram.federate_config.
    """

    version: str = "1.0"
    broker_config: bool = False


class ComponentDescription(BaseModel):
    """Component description for simple ComponentType.

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
    capabilities :
        Component capability declarations for build-time validation.
    """

    directory: str
    execute_function: str
    static_inputs: list[AnnotatedType]
    dynamic_inputs: list[AnnotatedType]
    dynamic_outputs: list[AnnotatedType]
    capabilities: ComponentCapabilities = Field(default_factory=ComponentCapabilities)


def types_to_dict(types: list[AnnotatedType]):
    return {t.port_name: t for t in types}


def component_from_json(filepath, type_checker):
    with open(filepath) as f:
        comp_desc = ComponentDescription.model_validate(json.load(f))
    return basic_component(comp_desc, type_checker)


def basic_component(comp_desc: ComponentDescription, type_checker):
    """Uses data in component_definition to create a new component type.

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
        _capabilities = comp_desc.capabilities

        def __init__(
            self,
            name,
            parameters: dict[str, Any],
            directory: str,
            host: str,
            port: int,
            comp_type: str,
            federate_config: HELICSFederateConfig | None = None,
        ):
            self._name = name
            self._directory = directory
            self._parameters = parameters
            self._federate_config = federate_config
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
            if self._federate_config is not None:
                self._parameters["federate_config"] = self._federate_config.to_dict()
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

        @property
        def broker_config_support(self):
            return self._capabilities.broker_config

    return BasicComponent
