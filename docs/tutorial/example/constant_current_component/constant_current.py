"""Tutorial component: a constant-current load that reacts to measured voltage.

Same three layers as power_component.py, plus a subscription that is decoded into
a Pydantic model before the algorithm sees it.
"""

from __future__ import annotations

import json
import logging

import helics as h
from oedisi.types import HELICSFederateConfig
from oedisi.types.data_types import PowersReal, VoltagesMagnitude

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def constant_current_power(
    base_power: list[float], base_voltage: float, voltage: list[float]
) -> list[float]:
    """Real power (kW) of a constant-current load: P = P_base * (V / V_base).

    This is the "I" term of the standard ZIP load model.
    """
    return [p * v / base_voltage for p, v in zip(base_power, voltage, strict=True)]


class ConstantCurrentConfig(HELICSFederateConfig):
    """Parameters read from static_inputs.json, on top of the HELICS settings."""

    node_ids: list[str]
    equipment_ids: list[str]
    base_power: list[float]
    base_voltage: float = 2400.0


class ConstantCurrentFederate:
    """HELICS value federate wrapping `constant_current_power`."""

    def __init__(self, config: ConstantCurrentConfig, input_mapping: dict[str, str]):
        self.config = config

        fedinfo = h.helicsCreateFederateInfo()
        config.apply_to_federate_info(fedinfo)
        self.fed = h.helicsCreateValueFederate(config.name, fedinfo)

        # `oedisi build` wrote the upstream publication key into input_mapping.json.
        self.sub_voltages = self.fed.register_subscription(input_mapping["voltages"], "")
        self.pub_power = self.fed.register_publication(
            "power", h.HELICS_DATA_TYPE_STRING, ""
        )

    def run(self) -> None:
        """React to each new voltage measurement until the federation ends."""
        self.fed.enter_executing_mode()

        # Driven by its input, so it asks for the end of time and lets HELICS wake
        # it whenever new data arrives.
        granted_time = self.fed.request_time(h.HELICS_TIME_MAXTIME)
        while granted_time < h.HELICS_TIME_MAXTIME:
            if self.sub_voltages.is_updated():
                voltages = VoltagesMagnitude.model_validate(self.sub_voltages.json)
                # We reorganize in the order of self.config.node_ids
                by_id = dict(zip(voltages.ids, voltages.values, strict=True))

                power = PowersReal(
                    values=constant_current_power(
                        self.config.base_power,
                        self.config.base_voltage,
                        [by_id[node] for node in self.config.node_ids],
                    ),
                    ids=self.config.node_ids,
                    equipment_ids=self.config.equipment_ids,
                    time=voltages.time,  # carry the measurement time through
                )
                self.pub_power.publish(power.model_dump_json())
                logger.info(
                    "t=%s published %s kW at %s", granted_time, power.values, power.time
                )

            granted_time = self.fed.request_time(h.HELICS_TIME_MAXTIME)

        self.fed.disconnect()


if __name__ == "__main__":
    with open("static_inputs.json") as f:
        config = ConstantCurrentConfig.model_validate(json.load(f))
    with open("input_mapping.json") as f:
        input_mapping = json.load(f)
    ConstantCurrentFederate(config, input_mapping).run()
