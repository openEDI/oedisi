""" """

from oedisi.types import HELICSFederateConfig
import helics as h
import logging
import json
import os

logger = logging.getLogger("uvicorn.error")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def destroy_federate(fed):
    _ = h.helicsFederateDisconnect(fed)
    h.helicsFederateFree(fed)
    h.helicsCloseLibrary()
    logger.info("Federate finalized")


class TestFederate:
    def __init__(self, config: HELICSFederateConfig):
        logger.info(config)
        logger.info(f"Current Working Directory: {os.path.abspath(os.curdir)}")
        fedinfo = h.helicsCreateFederateInfo()
        self.config = config
        config.apply_to_federate_info(fedinfo)
        logger.info(
            f"Federate connected to {config.broker.host}@{config.broker.port}"
        )

        self.fed = h.helicsCreateValueFederate(config.name, fedinfo)
        logger.info(f"Created federate {self.fed.name}")

        with open("input_mapping.json") as f:
            port_mapping = json.load(f)
            self.subscriptions = {}
            if "test1" in port_mapping:
                self.subscriptions["test1"] = self.fed.register_subscription(
                    port_mapping["test1"]
                )
            logger.debug(f"Loaded subscription test1 at {port_mapping['test1']}")

        self.publications = {}
        self.publications["test2"] = self.fed.register_publication(
            "test2", h.HELICS_DATA_TYPE_DOUBLE
        )

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
                value = 3.14159256535
                logger.info(f"Sending {value} to {name}")
                pub.publish(value)

            for name, sub in self.subscriptions.items():
                if sub.is_updated():
                    logger.info(f"From subscription {name}: {sub.bytes} of type {sub.type}")

        destroy_federate(self.fed)


if __name__ == "__main__":
    with open("static_inputs.json") as f:
        config = HELICSFederateConfig.model_validate_json(f.read())
    fed = TestFederate(config)
    fed.run()
