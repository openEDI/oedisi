from oedisi.componentframework.system_configuration import (
    generate_runner_config,
    WiringDiagram,
)
from oedisi.componentframework.mock_component import MockComponent
import json

component_types = {"MockComponent": MockComponent}
with open("test_system.json") as f:
    wiring_diagram = WiringDiagram.model_validate(json.load(f))
runner_config = generate_runner_config(
    wiring_diagram, component_types, target_directory="build"
)

with open("build/test_system_runner.json", "w") as f:
    f.write(runner_config.model_dump_json(indent=2))
