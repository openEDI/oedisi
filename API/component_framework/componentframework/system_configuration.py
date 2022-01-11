"""
Configuration Manager
"""

from collections import defaultdict
from typing import List, DefaultDict, Dict, Type, Any
import os
from abc import ABC, abstractmethod, abstractproperty
import json


class ComponentType(ABC):
    @abstractmethod
    def generate_input_mapping(self):
        pass

    @abstractproperty
    def execute_function(self):
        pass

    @abstractproperty
    def inputs(self):
        pass

    @abstractproperty
    def outputs(self):
        pass


class Component:
    def __init__(self, name: str, component_type: Type[ComponentType], parameters):
        self.name = name
        self.component_type = component_type
        self.parameters = parameters


class Link:
    def __init__(self, source: str, source_port: str, target: str, target_port: str):
        self.source = source
        self.source_port = source_port
        self.target = target
        self.target_port = target_port


def parse_component(component_json, component_types: Dict[str, Type[ComponentType]]):
    return Component(
        component_json["name"],
        component_types[component_json["component_type"]],
        component_json["parameters"],
    )


def parse_link(link_json):
    return Link(
        link_json["source"],
        link_json["source_port"],
        link_json["target"],
        link_json["target_port"],
    )


def parse_input(f, component_types: Dict[str, Type[ComponentType]]):
    """This function should take in the dataflow.
    This should generate a list of components and a list of links."""
    input_data = json.load(f)
    components = [
        parse_component(component_json, component_types)
        for component_json in input_data["components"]
    ]
    links = [parse_link(link_json) for link_json in input_data["links"]]
    return components, links


def check_names(components):
    "Check that the components all have unique names"
    names = set(map(lambda c: c.name, components))
    assert len(names) == len(components)


def connect(components: List[Component], links: List[Link]):
    check_names(components)
    component_map = {}
    for c in components:
        component_map[c.name] = c
    link_map = defaultdict(list)
    for link in links:
        link_map[link.target].append(link)
    return link_map


def generate_configs(
    components: List[Component], link_map: DefaultDict[str, List[Link]]
):
    federates = []
    for component in components:
        # Use component.component_type
        # Make a directory for each component
        directory = component.name
        if not os.path.exists(directory):
            os.mkdir(directory)
        initialized_component = component.component_type(
            component.name, component.parameters, directory
        )
        links = link_map[component.name]
        initialized_component.generate_input_mapping(
            {l.target_port: f"{l.source}/{l.source_port}" for l in links},
        )
        federate = {
            "directory": directory,
            "hostname": "localhost",
            "name": component.name,
            "exec": initialized_component.execute_function,
        }
        federates.append(federate)

    return federates


def generate_runner_config(name: str, federates: List[Any]):
    return {"name": name, "federates": federates}
