"""Tutorial component: publish scaled real power on a fixed schedule.

Three layers, kept separate: `scale_power` is the algorithm, `PowerComponentConfig`
is the configuration contract, and `PowerFederate` is the HELICS wrapper.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

import helics as h
from oedisi.types import HELICSFederateConfig
from oedisi.types.data_types import PowersReal

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def scale_power(base_power: list[float], multiplier: float) -> list[float]:
    """Scale each real power value (kW) by a static multiplier."""
    return [multiplier * p for p in base_power]


class PowerComponentConfig(HELICSFederateConfig):
    """Parameters read from static_inputs.json, on top of the HELICS settings."""

    node_ids: list[str]
    equipment_ids: list[str]
    base_power: list[float]
    multiplier: float = 1.0
    number_of_timesteps: int = 4
    step_size_seconds: float = 900.0
    start_time: datetime = datetime(2017, 1, 1)


class PowerFederate:
    """HELICS value federate wrapping `scale_power`."""

    def __init__(self, config: PowerComponentConfig):
        self.config = config

        fedinfo = h.helicsCreateFederateInfo()
        config.apply_to_federate_info(fedinfo)
        self.fed = h.helicsCreateValueFederate(config.name, fedinfo)

        # Non-global publication: the key other federates see is "<name>/power".
        self.pub_power = self.fed.register_publication(
            "power", h.HELICS_DATA_TYPE_STRING, ""
        )

    def run(self) -> None:
        """Publish one PowersReal per timestep, then disconnect."""
        self.fed.enter_executing_mode()

        for step in range(self.config.number_of_timesteps):
            # No inputs, so this federate steps the clock itself.
            granted_time = self.fed.request_time(step + 1)

            power = PowersReal(
                values=scale_power(self.config.base_power, self.config.multiplier),
                ids=self.config.node_ids,
                equipment_ids=self.config.equipment_ids,
                time=self.config.start_time
                + timedelta(seconds=step * self.config.step_size_seconds),
            )
            self.pub_power.publish(power.model_dump_json())
            logger.info(
                "t=%s published %s kW at %s", granted_time, power.values, power.time
            )

        self.fed.disconnect()


if __name__ == "__main__":
    with open("static_inputs.json") as f:
        config = PowerComponentConfig.model_validate(json.load(f))
    PowerFederate(config).run()
