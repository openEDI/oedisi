"""Unit tests for broker configuration generation and HELICS config types."""

import json
import pytest
from pathlib import Path
from oedisi.componentframework.system_configuration import (
    generate_runner_config,
    WiringDiagram,
    Component,
)
from oedisi.componentframework.mock_component import MockComponent
from oedisi.types.helics_config import SharedFederateConfig, HELICSBrokerConfig, HELICSFederateConfig
from oedisi.types.common import BrokerConfig


def make_diagram(num_components=1, shared_helics_config=None, component_params=None):
    """Create a wiring diagram with mock components."""
    if component_params is None:
        component_params = {"inputs": [], "outputs": {}}

    components = [
        Component(
            name=f"comp{i+1}",
            type="MockComponent",
            parameters=component_params,
        )
        for i in range(num_components)
    ]
    return WiringDiagram(
        name="test",
        components=components,
        links=[],
        shared_helics_config=shared_helics_config,
    )


def get_broker_cmd(wiring_diagram, **kwargs):
    """Generate runner config and return broker command."""
    runner_config = generate_runner_config(
        wiring_diagram,
        {"MockComponent": MockComponent},
        **kwargs,
    )
    return runner_config.federates[-1].exec


def test_broker_command_without_config():
    """Test that broker command is generated correctly without shared_helics_config."""
    diagram = make_diagram()
    broker_cmd = get_broker_cmd(diagram)
    assert broker_cmd == "helics_broker -f 1 --loglevel=warning"


def test_broker_command_with_core_type():
    """Test that broker command includes core type from shared_helics_config."""
    diagram = make_diagram(shared_helics_config=SharedFederateConfig(core_type="tcp"))
    broker_cmd = get_broker_cmd(diagram)

    assert "-t tcp" in broker_cmd
    assert "helics_broker" in broker_cmd
    assert "-f 1" in broker_cmd
    assert "--loglevel=warning" in broker_cmd


def test_broker_command_with_full_config():
    """Test that broker command includes all broker settings."""
    diagram = make_diagram(
        num_components=2,
        shared_helics_config=SharedFederateConfig(
            core_type="zmq",
            broker=HELICSBrokerConfig(port=23456, key="test_key"),
        ),
    )
    broker_cmd = get_broker_cmd(diagram)
    assert broker_cmd == "helics_broker -f 2 -t zmq --port 23456 --brokerkey test_key --loglevel=warning"


def test_broker_command_with_initstring():
    """Test that broker command includes initstring."""
    diagram = make_diagram(
        shared_helics_config=SharedFederateConfig(
            core_type="zmq",
            broker=HELICSBrokerConfig(initstring="--local_interface=127.0.0.1"),
        ),
    )
    broker_cmd = get_broker_cmd(diagram)
    assert "--local_interface=127.0.0.1" in broker_cmd


def test_component_config_includes_broker_settings(tmp_path: Path):
    """Test that component helics_config.json includes broker settings."""
    # Use custom component name for this test
    diagram = WiringDiagram(
        name="test",
        components=[
            Component(
                name="testcomp",
                type="MockComponent",
                parameters={"inputs": [], "outputs": {"voltage": "double"}},
            ),
        ],
        links=[],
        shared_helics_config=SharedFederateConfig(
            core_type="zmq",
            broker=HELICSBrokerConfig(port=23456, key="test_key"),
        ),
    )
    generate_runner_config(
        diagram,
        {"MockComponent": MockComponent},
        target_directory=str(tmp_path),
    )

    config_path = tmp_path / "testcomp" / "helics_config.json"
    assert config_path.exists()

    with open(config_path) as f:
        config = json.load(f)

    assert config["name"] == "testcomp"
    assert config["coreType"] == "zmq"
    assert config["broker"]["port"] == 23456
    assert config["broker"]["key"] == "test_key"


def test_component_without_broker_capability_raises_error():
    """Test that using shared_helics_config with unsupported component raises error."""
    from oedisi.componentframework.system_configuration import (
        ComponentType,
        ComponentCapabilities,
    )
    from oedisi.types.helics_config import HELICSFederateConfig

    class UnsupportedComponent(ComponentType):
        _capabilities = ComponentCapabilities(broker_config=False)

        def __init__(self, base_config: HELICSFederateConfig, parameters: dict,
                     directory: str, host: str | None = None, port: int | None = None,
                     comp_type: str | None = None):
            pass

        def generate_input_mapping(self, links):
            pass

        @property
        def execute_function(self):
            return "dummy"

        @property
        def dynamic_inputs(self):
            return {}

        @property
        def dynamic_outputs(self):
            return {}

    diagram = WiringDiagram(
        name="test",
        components=[Component(name="comp1", type="UnsupportedComponent", parameters={})],
        links=[],
        shared_helics_config=SharedFederateConfig(core_type="zmq"),
    )

    with pytest.raises(ValueError, match="does not support HELICS configuration"):
        generate_runner_config(diagram, {"UnsupportedComponent": UnsupportedComponent})


# HELICS Config Type Tests

def test_broker_config_from_rest_config():
    """Test conversion from REST API BrokerConfig to HELICSBrokerConfig."""
    rest_config = BrokerConfig(broker_ip="192.168.1.1", broker_port=23456)
    helics_config = HELICSBrokerConfig.from_rest_config(rest_config)

    assert helics_config.host == "192.168.1.1"
    assert helics_config.port == 23456


def test_shared_federate_config_to_federate_config():
    """Test conversion from SharedFederateConfig to HELICSFederateConfig."""
    shared = SharedFederateConfig(
        core_type="tcp",
        broker=HELICSBrokerConfig(port=23456, key="mykey"),
    )
    federate = shared.to_federate_config(name="test_fed", core_name="test_core")

    assert federate.name == "test_fed"
    assert federate.core_name == "test_core"
    assert federate.core_type == "tcp"
    assert federate.broker.port == 23456
    assert federate.broker.key == "mykey"


def test_federate_config_from_multicontainer():
    """Test creating federate config for multicontainer deployments."""
    broker_config = BrokerConfig(broker_ip="broker-service", broker_port=23456)
    params = {"name": "my_component", "some_param": "value"}

    config = HELICSFederateConfig.from_multicontainer(broker_config, params)

    assert config.name == "my_component"
    assert config.core_type == "zmq"
    assert config.broker.host == "broker-service"
    assert config.broker.port == 23456


def test_federate_config_serialization():
    """Test HELICSFederateConfig to_dict and to_json methods."""
    config = HELICSFederateConfig(
        name="test",
        core_type="zmq",
        broker=HELICSBrokerConfig(port=23456),
    )

    # Test to_dict with camelCase keys
    config_dict = config.to_dict()
    assert config_dict["name"] == "test"
    assert config_dict["coreType"] == "zmq"
    assert config_dict["broker"]["port"] == 23456

    # Test to_json
    config_json = config.to_json()
    assert "coreType" in config_json
    assert json.loads(config_json)["name"] == "test"


def test_apply_to_federate_info():
    """Test applying HELICSFederateConfig to a HELICS FederateInfo object."""
    import helics as h

    config = HELICSFederateConfig(
        name="test_fed",
        core_type="zmq",
        core_name="test_core",
        core_init_string="--federates=1",
        broker=HELICSBrokerConfig(host="localhost", port=23456, key="testkey"),
    )

    fed_info = h.helicsCreateFederateInfo()
    config.apply_to_federate_info(fed_info)  # Should not raise

    # FederateInfo properties are write-only. For end-to-end validation, see
    # tests/test_broker_integration which uses helicsCreateValueFederateFromConfig
    # to load the config file (as done in MockFederate).
    h.helicsFederateInfoFree(fed_info)
