#!/usr/bin/env python3
from componentframework.basic_component import basic_component
from componentframework.system_configuration import (
    generate_runner_config,
    parse_input,
    connect,
    generate_configs,
)
from componentframework.mock_component import MockComponent
import json

with open('test_component_type/component_definition.json') as f:
    component_definition = json.load(f)

TestComponent = basic_component(component_definition)
component_types = {
    "TestComponent": TestComponent,
    "MockComponent": MockComponent
}

with open("test_basic_system.json") as f:
    components, links = parse_input(f, component_types)

link_map = connect(components, links)
federates = generate_configs(components, link_map)

with open("test_basic_system_runner.json", "w") as f:
    json.dump(generate_runner_config("test_basic_system_configuration", federates), f)
