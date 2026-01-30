"""
Define common types and methods for configuration.

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
from typing import Any
import os
import logging
import shutil
import psutil
from abc import ABC, abstractmethod

from pydantic import field_validator, BaseModel, ValidationInfo
from oedisi.types.common import DOCKER_HUB_USER, APP_NAME
from oedisi.types.helics_config import HELICSFederateConfig, SharedFederateConfig


class AnnotatedType(BaseModel):
    """Represent the type on component static input, dynamic input, and dynamic output.

    Currently not checked in any type checker.
    """

    type: str
    "Name referencing oedisi Pydantic type or empty string"
    description: str | None = None
    unit: str | None = None
    port_id: str | None = None
    "Manually set port id"

    @property
    def port_name(self):
        """Input or output name which defaults to type name or port_id."""
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
    def __init__(
        self,
        base_config: HELICSFederateConfig,
        parameters: dict[str, dict[str, str]],
        directory: str,
        host: str | None = None,
        port: int | None = None,
        comp_type: str | None = None,
    ):
        pass

    @abstractmethod
    def generate_input_mapping(self, links: dict[str, str]):
        """Generate input mapping from link target ports to HELICS subscription keys."""
        pass

    @property
    @abstractmethod
    def execute_function(self) -> str:
        """Command to execute the component federate."""
        pass

    @property
    @abstractmethod
    def dynamic_inputs(self) -> dict[str, AnnotatedType]:
        """Dictionary of dynamic input port names to types."""
        pass

    @property
    @abstractmethod
    def dynamic_outputs(self) -> dict[str, AnnotatedType]:
        """Dictionary of dynamic output port names to types."""
        pass


class Link(BaseModel):
    """Connection between component ports in wiring diagram."""

    source: str
    "Name of component that is publishing"
    source_port: str
    "Publication/dynamic output name"
    target: str
    "Name of component that is subscribing"
    target_port: str
    "Dynamic input name mapped to source_port"


class Port(BaseModel):
    """Port identifier for creating links between components."""

    name: str
    "Component name"
    port_name: str
    "Dynamic input/output name"

    def connect(self, port: "Port") -> Link:
        """Create link from this port to target port.

        Parameters
        ----------
        self : Port
            Source port
        port : Port
            Target port

        Returns
        -------
        Link connecting self and port.
        """
        return Link(
            source=self.name,
            source_port=self.port_name,
            target=port.name,
            target_port=port.port_name,
        )


class Component(BaseModel):
    """A component configuration in WiringDiagram."""

    name: str
    "Name or identifier of this component instance"
    type: str
    "Type of component referencing component type dictionary"
    host: str | None = None
    "Hostname used in Docker Compose and Kubernetes"
    container_port: int | None = None
    "Port used in Docker Compose and Kubernetes"
    image: str = ""
    "Image used in Docker Compose and Kubernetes"
    parameters: dict[str, Any]
    "Configuration passed onto each component."
    helics_config_override: SharedFederateConfig | None = None

    def port(self, port_name: str) -> Port:
        """Create Port object for connecting this component at a port name."""
        return Port(name=self.name, port_name=port_name)

    @field_validator("image", mode="before")
    @classmethod
    def validate_image(cls, image: str, info: ValidationInfo) -> str:
        """Add latest tag to name if not specified."""
        if not image:
            return f"{DOCKER_HUB_USER}/{APP_NAME}_{info.data['type']}:latest"
        return image


class ComponentStruct(BaseModel):
    """Component with its associated links for multi-container configuration."""

    component: Component
    links: list[Link]
    "All links with the component as target"


class WiringDiagram(BaseModel):
    """Cosimulation configuration. This may end up wrapped in another interface.

    Parameters
    ----------
    name :
        Name of the simulation.
    components :
        List of components in the simulation.
    links :
        List of links connecting component ports.
    shared_helics_config :
        Optional shared federate configuration applied to all components.
        Per-component values (name, core_name) are derived automatically.
    """

    name: str
    "Name of the simulation"
    components: list[Component]
    "Component configuration and types"
    links: list[Link]
    "List of links {source, source_port, target, target_port} between components"
    shared_helics_config: SharedFederateConfig | None = None

    def clean_model(self, target_directory=".") -> None:
        """Remove component directories, log files, and stray broker processes.

        Parameters
        ----------
        target_directory : str = "."
            Build folder with component directories and logs.
        """
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

        for proc in psutil.process_iter():
            if proc.name() == "helics_broker":
                proc.kill()

    @field_validator("components")
    @classmethod
    def check_component_names(cls, components):
        """Check that the components all have unique names."""
        names = set(map(lambda c: c.name, components))
        assert len(names) == len(components)
        return components

    @field_validator("links")
    @classmethod
    def check_link_names(cls, links, info: ValidationInfo):
        """Validate that link source and target components exist."""
        if "components" in info.data:
            components = info.data["components"]
            names = set(map(lambda c: c.name, components))
            for link in links:
                assert link.source in names and link.target in names
        return links

    def add_component(self, c: Component) -> None:
        """Add component to wiring diagram."""
        self.components.append(c)

    def add_link(self, link: Link) -> None:
        """Add link to wiring diagram."""
        self.links.append(link)

    def get_link_map(self) -> dict[str, Link]:
        """Create mapping from component names to their incoming links."""
        link_map = defaultdict(list)
        for link in self.links:
            link_map[link.target].append(link)
        return link_map

    @classmethod
    def empty(cls, name="unnamed"):
        """Create empty wiring diagram with no components or links."""
        return cls(name=name, components=[], links=[], shared_helics_config=None)


class Federate(BaseModel):
    """Federate configuration for HELICS CLI runner."""

    directory: str
    "Directory in which the execution should take place"
    hostname: str = "localhost"
    "Hostname for Docker Compose and Kubernetes"
    name: str
    "Name of component (used for logs)"
    exec: str
    "Command to start component"


def initialize_federates(
    wiring_diagram: WiringDiagram,
    component_types: dict[str, type[ComponentType]],
    compatability_checker,
    target_directory=".",
) -> list[Federate]:
    """Initialize all the federates.

    Extracts config and sends it to each Component in an initalization step,
    then finds all dynamic inputs and outputs and sends input mappings.

    Parameters
    ----------
    wiring_diagram
    component_types : dictionary of component type names to ComponentType class
    compatibility_checker : function from types to bool
        Check if source type is compatible with target_type
    target_directory : str | Path = "."
        Directory where all components should be initialized.

    Returns
    -------
    List of `Federate` run configuration

    Raises
    ------
    ComponentType classes may return errors on configuration.
    """
    components = {}
    link_map = wiring_diagram.get_link_map()
    for component in wiring_diagram.components:
        directory = os.path.join(target_directory, component.name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        component_type = component_types[component.type]

        # Generate per-component federate config
        federate_config = None
        if component.helics_config_override is not None:
            logging.warning(
                f"Component '{component.name}' uses federate_config_override. "
                "Per-component overrides can cause subtle timing issues."
            )
            federate_config = component.helics_config_override.to_federate_config(
                name=component.name
            )
        elif wiring_diagram.shared_helics_config is not None:
            federate_config = wiring_diagram.shared_helics_config.to_federate_config(
                name=component.name
            )

        initialized_component = component_type(
            federate_config,
            component.parameters,
            directory,
            component.host,
            component.container_port,
            component.type,
        )
        components[component.name] = initialized_component

    for link in wiring_diagram.links:
        source_types = components[link.source].dynamic_outputs
        target_types = components[link.target].dynamic_inputs
        assert link.source_port in source_types, (
            f"{link.source} does not have {link.source_port}"
        )
        assert link.target_port in target_types, (
            f"{link.target} does not have dynamic input {link.target_port}"
        )
        source_type = source_types[link.source_port]
        target_type = target_types[link.target_port]
        assert compatability_checker(source_type, target_type), (
            f"{source_type} is not compatible with {target_type}"
        )

    federates = []
    for name, component in components.items():
        links = link_map[name]
        component.generate_input_mapping(
            {link.target_port: f"{link.source}/{link.source_port}" for link in links}
        )

        federates.append(
            Federate(directory=name, name=name, exec=component.execute_function)
        )

    return federates


class RunnerConfig(BaseModel):
    """HELICS running config for the full simulation.

    Examples
    --------
    Save to JSON

    >>> with open(filename, "w") as f:
    ...    json.dump(config.model_dump(mode="json"), f)

    Run Simulation

    `$ helics run --path=filename`
    """

    name: str
    federates: list[Federate]


def _bad_compatability_checker(type1, type2):
    """Return True for all type pairs (no type checking)."""
    return True


def generate_runner_config(
    wiring_diagram: WiringDiagram,
    component_types: dict[str, type[ComponentType]],
    compatibility_checker=_bad_compatability_checker,
    target_directory=".",
):
    """Create HELICS run configuration from wiring diagram and component types.

    Parameters
    ----------
    wiring_diagram : WiringDiagram
        Configuration describing components, parameters, and links between them
    component_types : Dict[str, Type[ComponentType]]
        Dictionary for the wiring diagram component types
        to Python component types
    compatibility_checker: function of two types to a bool
        Each link uses the compatability_checker to ensure the link types are
        compatible.

    Returns
    -------
    RunnerConfig
        Configuration which can be used to run the cosimulation

    Raises
    ------
    Can raise any exception from component type initialization
    """
    federates = initialize_federates(
        wiring_diagram, component_types, compatibility_checker, target_directory
    )
    broker_federate = Federate(
        directory=".",
        name="broker",
        exec=f"helics_broker -f {len(federates)} --loglevel=warning",
    )
    return RunnerConfig(name=wiring_diagram.name, federates=([*federates, broker_federate]))
