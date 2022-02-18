"""
Configuration Manager
"""

from collections import defaultdict
from typing import List, Dict, Type, Any
import os
from abc import ABC, abstractmethod, abstractproperty

from pydantic import BaseModel, validator
from typing import List, Optional, Any, Dict


class AnnotatedType(BaseModel):
    "Class for representing types"
    type: str
    description: Optional[str]
    unit: Optional[str]
    port_id: Optional[str]

    @property
    def port_name(self):
        if self.port_id is None:
            return self.type
        return self.port_id


class ComponentType(ABC):
    @abstractmethod
    def generate_input_mapping(self):
        pass

    @abstractproperty
    def execute_function(self):
        pass

    @abstractproperty
    def dynamic_inputs(self):
        pass

    @abstractproperty
    def dynamic_outputs(self):
        pass


class Component(BaseModel):
    name: str
    type: str
    parameters: Dict[str, Any]


class Link(BaseModel):
    source: str
    source_port: str
    target: str
    target_port: str


class WiringDiagram(BaseModel):
    name: str
    components: List[Component]
    links: List[Link]

    @validator("components")
    def check_component_names(cls, components):
        "Check that the components all have unique names"
        names = set(map(lambda c: c.name, components))
        assert len(names) == len(components)
        return components

    @validator("links")
    def check_link_names(cls, links, values, **kwargs):
        if "components" in values:
            components = values["components"]
            names = set(map(lambda c: c.name, components))
            for link in links:
                assert link.source in names and link.target in names
        return links


class Federate(BaseModel):
    directory: str
    hostname = "localhost"
    name: str
    exec: str


def initialize_federates(
    wiring_diagram: WiringDiagram,
    component_types: Dict[str, Type[ComponentType]],
    compatability_checker,
) -> List[Federate]:
    components = {}
    link_map = get_link_map(wiring_diagram)
    for component in wiring_diagram.components:
        directory = component.name
        if not os.path.exists(directory):
            os.mkdir(directory)
        component_type = component_types[component.type]
        initialized_component = component_type(
            component.name, component.parameters, directory
        )
        components[component.name] = initialized_component

    for l in wiring_diagram.links:
        source_types = components[l.source].dynamic_outputs
        target_types = components[l.target].dynamic_inputs
        assert (
            l.source_port in source_types
        ), f"{l.source} does not have {l.source_port}"
        assert (
            l.target_port in target_types
        ), f"{l.target} does not have {l.target_port}"
        source_type = source_types[l.source_port]
        target_type = target_types[l.target_port]
        assert compatability_checker(
            source_type, target_type
        ), f"{source_type} is not compatible with {target_type}"

    federates = []
    for name, component in components.items():
        links = link_map[name]
        component.generate_input_mapping(
            {l.target_port: f"{l.source}/{l.source_port}" for l in links}
        )
        federates.append(
            Federate(directory=name, name=name, exec=component.execute_function)
        )

    return federates


def get_link_map(wiring_diagram: WiringDiagram):
    link_map = defaultdict(list)
    for link in wiring_diagram.links:
        link_map[link.target].append(link)
    return link_map


class RunnerConfig(BaseModel):
    name: str
    federates: List[Federate]


def bad_compatability_checker(type1, type2):
    return True


def generate_runner_config(
    wiring_diagram: WiringDiagram,
    component_types: Dict[str, Type[ComponentType]],
    compatability_checker=bad_compatability_checker,
):
    federates = initialize_federates(
        wiring_diagram, component_types, compatability_checker
    )
    broker_federate = Federate(
        directory=".",
        name="broker",
        exec="helics_broker -f {len(federates)} --loglevel=warning",
    )
    return RunnerConfig(
        name=wiring_diagram.name, federates=(federates + [broker_federate])
    )