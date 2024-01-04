from oedisi.componentframework.system_configuration import (
    generate_runner_config,
    WiringDiagram,
)
from oedisi.componentframework.mock_component import MockComponent
import json

component_types = {"MockComponent": MockComponent}
wiring_diagram = WiringDiagram.parse_file("test_system.json")
runner_config = generate_runner_config(
    wiring_diagram, component_types, target_directory="build"
)

with open("build/test_system_runner.json", "w") as f:
    f.write(runner_config.json(indent=2))
