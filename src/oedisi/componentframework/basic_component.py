"""Generate basic component from description JSON."""

import json
import os
from shutil import copytree
from typing import Any

from pydantic import BaseModel, Field

from . import system_configuration
from .system_configuration import AnnotatedType, ComponentCapabilities
from oedisi.types.helics_config import HELICSFederateConfig


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
    "Where code is stored relative to where this is run"
    execute_function: str
    "Command to execute component"
    static_inputs: list[AnnotatedType]
    "List of types for the parameter"
    dynamic_inputs: list[AnnotatedType]
    "List of input types. Typically subscriptions."
    dynamic_outputs: list[AnnotatedType]
    "List of output types. Typically publications."
    capabilities: ComponentCapabilities = Field(default_factory=ComponentCapabilities)


def _types_to_dict(types: list[AnnotatedType]) -> dict[str, AnnotatedType]:
    """Convert list of annotated types to dictionary keyed by port name."""
    return {t.port_name: t for t in types}


def component_from_json(filepath, type_checker):
    """Load component description from JSON file and create component type.

    Parameters
    ----------
    filepath : str | Path
    type_checker : function taking the type and value and returning a boolean

    Returns
    -------
    BasicComponent class
    """
    with open(filepath) as f:
        comp_desc = ComponentDescription.model_validate(json.load(f))
    return basic_component(comp_desc, type_checker)


def basic_component(comp_desc: ComponentDescription, type_checker):
    """Create a new component type from component definition data.

    Parameters
    ----------
    comp_desc : ComponentDescription
         Simplified component representation usually from a JSON file
    type_checker : function taking the type and value and returning a boolean

    Returns
    -------
    BasicComponent(system_configuration.ComponentType) :
         ComponentType from the description
    """

    class BasicComponent(system_configuration.ComponentType):
        _origin_directory = comp_desc.directory
        _execute_function = comp_desc.execute_function
        _dynamic_inputs = _types_to_dict(comp_desc.dynamic_inputs)
        _dynamic_outputs = _types_to_dict(comp_desc.dynamic_outputs)
        _static_inputs = _types_to_dict(comp_desc.static_inputs)
        _capabilities = comp_desc.capabilities

        def __init__(
            self,
            base_config: HELICSFederateConfig,
            parameters: dict[str, Any],
            directory: str,
            host: str,
            port: int,
            comp_type: str,
        ):
            self._base_config = base_config
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
            if self.broker_config_support:
                config = self._base_config.to_dict() | self._parameters
            else:  # Backwards compatible behavior where we ignore extra information.
                config = self._parameters
                config["name"] = self._base_config.name
            with open(os.path.join(self._directory, "static_inputs.json"), "w") as f:
                json.dump(config, f)

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
