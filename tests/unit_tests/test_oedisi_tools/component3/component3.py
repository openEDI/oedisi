# -*- coding: utf-8 -*-
"""
"""

import helics as h
import logging
import json
import os
import time


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def destroy_federate(fed):
    _ = h.helicsFederateDisconnect(fed)
    h.helicsFederateFree(fed)
    h.helicsCloseLibrary()
    logger.info("Federate finalized")


class TestFederate:
    def __init__(self):
        logger.info(f"Current Working Directory: {os.path.abspath(os.curdir)}")
        with open("static_inputs.json") as f:
            self.parameters = json.load(f)

        time.sleep(3)
        fedinfo = h.helicsCreateFederateInfo()
        fedinfo.core_name = self.parameters["name"]
        fedinfo.core_type = h.HELICS_CORE_TYPE_ZMQ
        fedinfo.core_init = "--federates=1"

        self.fed = h.helicsCreateValueFederate(self.parameters["name"], fedinfo)
        logger.info(f"Created federate {self.fed.name}")

        time.sleep(3)
        with open("input_mapping.json", "r") as f:
            port_mapping = json.load(f)
            self.subscriptions = {}
            if "test1" in port_mapping:
                self.subscriptions["test1"] = self.fed.register_subscription(
                    port_mapping["test1"]
                )
            logging.debug("Loaded subscription test1 at {port_mapping['test1']}")

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

            for name, sub in self.subscriptions.items():
                if sub.is_updated():
                    logger.info(
                        f"From subscription {name}: {sub.bytes} of type {sub.type}"
                    )

        destroy_federate(self.fed)


if __name__ == "__main__":
    fed = TestFederate()
    fed.run()
