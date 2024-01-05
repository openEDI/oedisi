"""
MockComponent and MockFederate allow you to instantiate a mock component
with a specified set of inputs and outputs. The parameters dictionary
should contain a list under "inputs" and "outputs". During implementation,
the value pi is passed around every second until t=100.

MockComponent defines the ComponentType for a simple testing component.

MockFederate defines the corresponding implementation.
"""

import helics as h
import logging
from typing import Dict
import json
import os
from . import system_configuration
from .system_configuration import AnnotatedType


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class MockComponent(system_configuration.ComponentType):
    def __init__(
        self,
        name,
        parameters: Dict[str, Dict[str, str]],
        directory: str,
        host: str = None,
        port: int = None,
        comp_type: str = None,
    ):
        self._name = name
        self._directory = directory
        self._execute_function = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "mock_component.sh"
        )
        self.process_parameters(parameters)

    def process_parameters(self, parameters):
        self._dynamic_inputs = {
            name: AnnotatedType(type="", port_id=name) for name in parameters["inputs"]
        }
        self._dynamic_outputs = {
            name: AnnotatedType(type=type, port_id=name)
            for name, type in parameters["outputs"].items()
        }
        self.generate_helics_config(parameters["outputs"])

    def generate_helics_config(self, outputs):
        helics_config = {
            "name": self._name,
            "core_type": "zmq",
            "period": 1,
            "log_level": "warning",
            "terminate_on_error": True,
            "publications": [
                {"key": key, "type": value} for key, value in outputs.items()
            ],
        }

        with open(os.path.join(self._directory, "helics_config.json"), "w") as f:
            json.dump(helics_config, f)

    def generate_input_mapping(self, links):
        with open(os.path.join(self._directory, "input_mapping.json"), "w") as f:
            json.dump(links, f)

    @property
    def dynamic_inputs(self):
        return self._dynamic_inputs

    @property
    def dynamic_outputs(self):
        return self._dynamic_outputs

    @property
    def execute_function(self):
        return self._execute_function


def get_default_value(date_type: h.HelicsDataType):
    return 3.1415926536


def destroy_federate(fed):
    _ = h.helicsFederateDisconnect(fed)
    h.helicsFederateFree(fed)
    h.helicsCloseLibrary()
    logger.info("Federate finalized")


class MockFederate:
    def __init__(self):
        logger.info(f"Current Working Directory: {os.path.abspath(os.curdir)}")
        self.fed = h.helicsCreateValueFederateFromConfig("helics_config.json")
        logger.info(f"Created federate {self.fed.name}")

        with open("input_mapping.json", "r") as f:
            port_mapping = json.load(f)
            self.subscriptions = {}
            for name, key in port_mapping.items():
                self.subscriptions[name] = self.fed.register_subscription(key)
                logging.debug("Loaded subscription {name} at {key}")
            logging.info("Loaded all subscriptions from file")

    def run(self):
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
                    logger.info(
                        f"From subscription {name}: {sub.bytes} of type {sub.type}"
                    )

        destroy_federate(self.fed)


if __name__ == "__main__":
    fed = MockFederate()
    fed.run()
