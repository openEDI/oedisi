#!/usr/bin/env python3
from oedisi.componentframework.basic_component import component_from_json
from oedisi.componentframework.system_configuration import (
    generate_runner_config,
    WiringDiagram,
)
from oedisi.componentframework.mock_component import MockComponent


def bad_type_checker(type, x):
    return True


TestComponent = component_from_json(
    "test_component_type/component_definition.json", bad_type_checker
)
component_types = {"TestComponent": TestComponent, "MockComponent": MockComponent}

wiring_diagram = WiringDiagram.parse_file("test_basic_system.json")
runner_config = generate_runner_config(wiring_diagram, component_types)

with open("test_system_runner.json", "w") as f:
    f.write(runner_config.json(indent=2))
