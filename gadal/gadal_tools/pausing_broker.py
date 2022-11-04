import helics as h
import click
import time


class PausingBroker:
    def __init__(self, n):
        self.initstring = f"-f {n} --name=mainbroker"

    def run(self):
        self.broker = h.helicsCreateBroker("zmq", "", self.initstring)
        assert h.helicsBrokerIsConnected(self.broker) is True
        start_time = time.time()
        while time.time() - start_time < 10:
            h.helicsBrokerSetTimeBarrier(self.broker, 0.0)
