import time

import click
import helics as h
from .broker_utils import pprint_time_data, get_time_data


class PausingBroker:
    def __init__(self, n):
        self.initstring = f"-f {n} --name=mainbroker"

    def run(self):
        self.broker = h.helicsCreateBroker("zmq", "", self.initstring)
        print("Setting time barrier to 0.0")
        h.helicsBrokerSetTimeBarrier(self.broker, 0.0)
        t = 0.0

        time.sleep(3)
        name_2_timedata = {}
        while h.helicsBrokerIsConnected(self.broker) is True:
            for time_data in get_time_data(self.broker):
                if (time_data.name not in name_2_timedata) or (
                    name_2_timedata[time_data.name] != time_data
                ):
                    name_2_timedata[time_data.name] = time_data
                    pprint_time_data(time_data)

            new_t = click.prompt("Enter next time:", type=float, default=t)
            if new_t != t:
                t = new_t
                print(f"Setting time barrier to {t}")
                h.helicsBrokerSetTimeBarrier(self.broker, t)
