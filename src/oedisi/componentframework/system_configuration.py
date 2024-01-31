"""
This module defines common types and methods for configuration.

The final method `generate_runner_config` brings together
a `WiringDiagram` and a dictionary of `ComponentTypes` with
optional comparison using a compatability checking function.

The `ComponentType` defines the common interface that component
configuration must implement. By default, this can be instantiated
using `basic_component.py`.

The `WiringDiagram` configuration contains a list of components
and the links between them.
"""

from collections import defaultdict
from typing import List, Dict, Type, Any
import os
import logging
import shutil
import psutil
from abc import ABC, abstractmethod, abstractproperty

from pydantic import BaseModel, validator
from typing import List, Optional, Any, Dict
from oedisi.types.common import DOCKER_HUB_USER, APP_NAME


class AnnotatedType(BaseModel):
    "Class for representing the types of components and their interfaces"
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
    """Abstract type for component configuration.

    The components define the main restrictions on how components
    can be configured. In the simplest case, the `basic_copmonent` function
    constructs a type from a `ComponentDescription` which just write files.
    There are no restrictions, so for example, one possibility is for the component type
    to interact with a web service.

    First, the class is initialized for each component using the
    name, parameters, and target directory. The federate name
    in HELICS should be the name initialized here.

    Then the `dynamic_inputs` and `dynamic_outputs` are used to check types and verify
    the links used between components. These can depend on the initialziation parameters.
    The `dynamic_outputs` should be initialized under the prefix `name/`.

    Next, `generate_input_mapping` is then called with a mapping
    of the variable names to the HELICS subscription keys. The individual
    federate should then use these names to subscribe at the right location.
    This can also be used for endpoint targets less often.

    Finally, the execute_function property defines the command
    to run the component.
    """

    @abstractmethod
    def generate_input_mapping(self, links: Dict[str, str]):
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


class Link(BaseModel):
    source: str
    source_port: str
    target: str
    target_port: str


class Port(BaseModel):
    name: str
    port_name: str

    def connect(self, port: "Port"):
        return Link(
            source=self.name,
            source_port=self.port_name,
            target=port.name,
            target_port=port.port_name,
        )


class Component(BaseModel):
    """Component type used in WiringDiagram, includes name,
    component type, and initial parameters"""

    name: str
    type: str
    host: Optional[str]
    container_port: Optional[int]
    image: str = ""
    parameters: Dict[str, Any]

    def port(self, port_name: str):
        return Port(name=self.name, port_name=port_name)

    @validator("image", pre=True, always=True)
    def validate_image(cls, v, values, **kwargs):
        if not v:
            return f"{DOCKER_HUB_USER}/{APP_NAME}_{values['name']}:latest"
        return v


class WiringDiagram(BaseModel):
    "Cosimulation configuration. This may end up wrapped in another interface"
    name: str
    components: List[Component]
    links: List[Link]

    def clean_model(self, target_directory="."):
        for component in self.components:
            to_delete = os.path.join(target_directory, component.name)
            log_file = os.path.join(target_directory, component.name + ".log")
            if not os.path.exists(to_delete):
                logging.warning(
                    f"The directory for {component.name} at {to_delete} does not exist"
                )
            else:
                shutil.rmtree(to_delete)
            if not os.path.exists(log_file):
                logging.warning(
                    f"The directory for {component.name} at {log_file} does not exist"
                )
            else:
                os.remove(log_file)

        # TODO: Check for any processes using the HELICS port and kill them too
        for proc in psutil.process_iter():
            if proc.name() == "helics_broker":
                proc.kill()

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

    def add_component(self, c: Component):
        self.components.append(c)

    def add_link(self, l: Link):
        self.links.append(l)

    @classmethod
    def empty(cls, name="unnamed"):
        return cls(name=name, components=[], links=[])


class Federate(BaseModel):
    "Federate configuration for HELICS CLI"
    directory: str
    hostname: str = "localhost"
    name: str
    exec: str


def get_federates_conn_info(wiring_diagram: WiringDiagram):
    data = ""
    for component in wiring_diagram.components:
        data += f" {component.host} {component.port}"
    return data


def initialize_federates(
    wiring_diagram: WiringDiagram,
    component_types: Dict[str, Type[ComponentType]],
    compatability_checker,
    target_directory=".",
) -> List[Federate]:
    "Initialize all the federates"
    components = {}
    link_map = get_link_map(wiring_diagram)
    for component in wiring_diagram.components:
        directory = os.path.join(target_directory, component.name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        component_type = component_types[component.type]
        initialized_component = component_type(
            component.name,
            component.parameters,
            directory,
            component.host,
            component.port,
            component.type,
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
        ), f"{l.target} does not have dynamic input {l.target_port}"
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
    """HELICS running config for the full simulation

    Examples
    --------
    Save to JSON

    >>> with open(filename, "w") as f:
    ...    f.write(config.json())

    Run Simulation

    `$ helics run --path=filename`
    """

    name: str
    federates: List[Federate]


def bad_compatability_checker(type1, type2):
    "Basic compatability checker that says all types are compatible."
    return True


def generate_runner_config(
    wiring_diagram: WiringDiagram,
    component_types: Dict[str, Type[ComponentType]],
    compatibility_checker=bad_compatability_checker,
    target_directory=".",
):
    """Brings together a `WiringDiagram` and a dictionary of `ComponentTypes`
    to create a helics run configuration.

    Parameters
    ----------
    wiring_diagram : WiringDiagram
        Configuration describing components, parameters, and links between them
    component_types : Dict[str, Type[ComponentType]]
        Dictionary for the wiring diagram component types
        to Python component types
    compatibility_checker: function of two types to the booleans
        Each link uses the compatability_checker to ensure the link
        is between compatible types.

    Returns
    -------
    RunnerConfig
        Configuration which can be used to run the cosimulation
    """
    federates = initialize_federates(
        wiring_diagram, component_types, compatibility_checker, target_directory
    )
    broker_federate = Federate(
        directory=".",
        name="broker",
        exec=f"helics_broker -f {len(federates)} --loglevel=warning",
    )
    return RunnerConfig(
        name=wiring_diagram.name, federates=(federates + [broker_federate])
    )
