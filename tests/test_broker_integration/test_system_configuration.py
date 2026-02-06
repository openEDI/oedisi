"""Generate runner configuration for broker integration test."""

import json
from oedisi.componentframework.system_configuration import (
    generate_runner_config,
    WiringDiagram,
)
from oedisi.componentframework.mock_component import MockComponent

component_types = {"MockComponent": MockComponent}

with open("system.json") as f:
    wiring_diagram = WiringDiagram.model_validate(json.load(f))

runner_config = generate_runner_config(
    wiring_diagram, component_types, target_directory="build"
)

with open("build/system_runner.json", "w") as f:
    f.write(runner_config.model_dump_json(indent=2))

# Verify broker command includes custom configuration
broker_cmd = runner_config.federates[-1].exec
print(f"Generated broker command: {broker_cmd}")

assert "-t zmq" in broker_cmd, "Broker command missing core type"
assert "--port 23408" in broker_cmd, "Broker command missing custom port"
assert "--brokerkey integration_test_key" in broker_cmd, "Broker command missing broker key"

# Verify component configs include broker settings
for component_name in ["sender", "receiver"]:
    config_path = f"build/{component_name}/helics_config.json"
    with open(config_path) as f:
        config = json.load(f)

    assert config["coreType"] == "zmq", f"{component_name} missing core type"
    assert "broker" in config, f"{component_name} missing broker config"
    assert config["broker"]["port"] == 23408, f"{component_name} has wrong broker port"
    print(f"✓ {component_name} config verified")

print("✓ All configuration checks passed")
