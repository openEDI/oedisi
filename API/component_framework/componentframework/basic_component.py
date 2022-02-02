# -*- coding: utf-8 -*-
"""
"""

import helics as h
from typing import Dict, Any
import json
import os
from shutil import copytree
from . import system_configuration


def basic_component(component_definition: Dict[str, Any]):
    """
    Uses data in component_definition to create a new component type
    """
    class BasicComponent(system_configuration.ComponentType):
        _origin_directory = component_definition["directory"]
        _execute_function = component_definition["execute_function"]
        _inputs = component_definition["inputs"]
        _outputs = component_definition["outputs"]
        def __init__(self, name, parameters: Dict[str, Dict[str, str]], directory: str):
            self._name = name
            self._directory = directory
            self._parameters = parameters
            self.copy_code_into_directory()
            self.generate_parameter_config()

        def copy_code_into_directory(self):
            copytree(self._origin_directory, self._directory, dirs_exist_ok=True)

        def generate_parameter_config(self):
            self._parameters["name"] = self._name
            with open(os.path.join(self._directory, "parameters.json"), "w") as f:
                json.dump(self._parameters, f)

        def generate_input_mapping(self, links):
            with open(os.path.join(self._directory, "inputs.json"), "w") as f:
                json.dump(links, f)

        @property
        def inputs(self):
            return self._inputs

        @property
        def outputs(self):
            return self._outputs

        @property
        def execute_function(self):
            return self._execute_function

    return BasicComponent
