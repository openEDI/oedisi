import time

import click
import helics as h
from pydantic import BaseModel

class TimeData(BaseModel):
    "Time data for a federate"
    name: str
    granted_time: float
    send_time: float


def pprint_time_data(time_data):
    "A table would be better somehow, but which should be the columns"
    print(f"""
    Name         : {time_data.name}
    Granted Time : {time_data.granted_time}
    Send Time    : {time_data.send_time}
    """)


def parse_time_data(response):
    time_data = []
    for core in response["cores"]:
        for fed in core["federates"]:
            time_data.append(TimeData(
                name = fed["attributes"]["name"],
                granted_time = fed["granted_time"],
                send_time = fed["send_time"]
            ))

    return time_data


class PausingBroker:
    def __init__(self, n):
        self.initstring = f"-f {n} --name=mainbroker"

    def run(self):
        self.broker = h.helicsCreateBroker("zmq", "", self.initstring)
        print("Setting time barrier to 0.0")
        h.helicsBrokerSetTimeBarrier(self.broker, 0.0)
        t = 0.0
        time.sleep(2)
        while h.helicsBrokerIsConnected(self.broker) is True:
            for t_data in parse_time_data(
                    self.broker.query("broker", "global_time")
                    ):
                pprint_time_data(t_data)
            t = click.prompt('Enter next time:', type=float, default=t+1)
            print(f"Setting time barrier to {t}")
            h.helicsBrokerSetTimeBarrier(self.broker, t)
