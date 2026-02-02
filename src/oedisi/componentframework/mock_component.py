"""Mock component and federate for testing HELICS simulations.

MockComponent and MockFederate allow you to instantiate a mock component
with a specified set of inputs and outputs. The parameters dictionary
should contain a list under "inputs" and "outputs". During implementation,
the value pi is passed around every second until t=100.

MockComponent defines the ComponentType for a simple testing component.

MockFederate defines the corresponding implementation.
"""

import helics as h
import logging
import json
import os
from . import system_configuration
from .system_configuration import AnnotatedType


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class MockComponent(system_configuration.ComponentType):
    """Mock component for testing HELICS-based simulations.

    Provides a configurable mock component with dynamic inputs and outputs
    for use in testing and validation scenarios.

    Parameters
    ----------
    name : str
        Name of the mock component.
    parameters : dict[str, dict[str, str]]
        Configuration parameters containing "inputs" and "outputs" keys.
    directory : str
        Working directory for component configuration files.
    host : str, optional
        Host address (not used in mock implementation).
    port : int, optional
        Port number (not used in mock implementation).
    comp_type : str, optional
        Component type identifier (not used in mock implementation).
    """

    def __init__(
        self,
        name,
        parameters: dict[str, dict[str, str]],
        directory: str,
        host: str | None = None,
        port: int | None = None,
        comp_type: str | None = None,
    ):
        self._name = name
        self._directory = directory
        self._execute_function = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "mock_component.sh"
        )
        self.process_parameters(parameters)

    def process_parameters(self, parameters):
        """Process and configure component parameters.

        Parameters
        ----------
        parameters : dict[str, dict[str, str]]
            Configuration dictionary with "inputs" and "outputs" keys.
        """
        self._dynamic_inputs = {
            name: AnnotatedType(type="", port_id=name) for name in parameters["inputs"]
        }
        self._dynamic_outputs = {
            name: AnnotatedType(type=type, port_id=name)
            for name, type in parameters["outputs"].items()
        }
        self.generate_helics_config(parameters["outputs"])

    def generate_helics_config(self, outputs):
        """Generate HELICS configuration file for the mock component.

        Parameters
        ----------
        outputs : dict[str, str]
            Mapping of output port names to HELICS data types.
        """
        helics_config = {
            "name": self._name,
            "core_type": "zmq",
            "period": 1,
            "log_level": "warning",
            "terminate_on_error": True,
            "publications": [{"key": key, "type": value} for key, value in outputs.items()],
        }

        with open(os.path.join(self._directory, "helics_config.json"), "w") as f:
            json.dump(helics_config, f)

    def generate_input_mapping(self, links):
        """Generate input mapping file for subscriptions.

        Parameters
        ----------
        links : dict
            Mapping of local input port names to HELICS subscription keys.
        """
        with open(os.path.join(self._directory, "input_mapping.json"), "w") as f:
            json.dump(links, f)

    @property
    def dynamic_inputs(self):
        """Dynamic input ports."""
        return self._dynamic_inputs

    @property
    def dynamic_outputs(self):
        """Dynamic output ports."""
        return self._dynamic_outputs

    @property
    def execute_function(self):
        """Path to mock component execution script."""
        return self._execute_function


def get_default_value(date_type: h.HelicsDataType):
    """Return pi value for mock publications."""
    return 3.1415926536


def destroy_federate(fed):
    """Disconnect and free a HELICS federate."""
    _ = h.helicsFederateDisconnect(fed)
    h.helicsFederateFree(fed)
    h.helicsCloseLibrary()
    logger.info("Federate finalized")


class MockFederate:
    """Mock HELICS federate for testing simulations.

    Loads configuration and subscriptions from files, then publishes
    test values during simulation.
    """

    def __init__(self):
        """Initialize mock federate from HELICS and input mapping configs."""
        logger.info(f"Current Working Directory: {os.path.abspath(os.curdir)}")
        self.fed = h.helicsCreateValueFederateFromConfig("helics_config.json")
        logger.info(f"Created federate {self.fed.name}")

        with open("input_mapping.json") as f:
            port_mapping = json.load(f)
            self.subscriptions = {}
            for name, key in port_mapping.items():
                self.subscriptions[name] = self.fed.register_subscription(key)
                logging.debug("Loaded subscription {name} at {key}")
            logging.info("Loaded all subscriptions from file")

    def run(self):
        """Execute simulation, publishing values for 100 seconds."""
        self.fed.enter_executing_mode()
        logger.info("Entered HELICS execution mode")

        total_interval = 100
        update_interval = 1
        grantedtime = 0
        while grantedtime < total_interval:
            requested_time = grantedtime + update_interval
            logger.debug(f"Requesting time {requested_time}")
            grantedtime = self.fed.request_time(requested_time)
            logger.debug(f"Granted time {grantedtime}")

            for name, pub in self.fed.publications.items():
                value = get_default_value(pub.type)
                logger.info(f"Sending {value} to {name}")
                pub.publish(value)

            for name, sub in self.subscriptions.items():
                if sub.is_updated():
                    logger.info(f"From subscription {name}: {sub.bytes} of type {sub.type}")

        destroy_federate(self.fed)


if __name__ == "__main__":
    fed = MockFederate()
    fed.run()
