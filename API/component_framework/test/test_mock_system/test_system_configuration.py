from componentframework.system_configuration import (
    generate_runner_config,
    parse_input,
    connect,
    generate_configs,
)
from componentframework.mock_component import MockComponent
import json

component_types = {"MockComponent": MockComponent}

with open("test_system.json") as f:
    components, links = parse_input(f, component_types)

link_map = connect(components, links)
federates = generate_configs(components, link_map)

with open("test_system_runner.json", "w") as f:
    json.dump(generate_runner_config("test_system_configation", federates), f)
