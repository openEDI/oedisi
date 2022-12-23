import time

import click
import helics as h
from pydantic import BaseModel
from typing import List, Dict, Tuple
import json


def get_inputs_outputs(graph_dict):
    federate_inputs = {}
    federate_outputs = {}
    federate_id_handle2key = {}

    federate_id2name = {}
    for c in graph_dict["cores"]:
        for fed in c["federates"]:
            name = fed["attributes"]["name"]
            federate_id2name[
                fed["attributes"]["id"]
            ] = name
            pub_keys = []
            for pub in fed["publications"]:
                federate_id_handle2key[
                    (pub["federate"], pub["handle"])
                ] = pub["key"]
                pub_keys.append(pub["key"])
            federate_outputs[name] = pub_keys

    for c in graph_dict["cores"]:
        for fed in c["federates"]:
            name = fed["attributes"]["name"]
            sub_keys = []
            for sub in fed["inputs"]:
                for source in sub["sources"]:
                    sub_keys.append(federate_id_handle2key[
                        (source["federate"], source["handle"])
                    ])
            federate_inputs[name] = sub_keys
    return federate_inputs, federate_outputs


class TestingBroker:
    def __init__(self, n):
        self.initstring = f"-f {n} --name=mainbroker"

    def run(self):
        time.sleep(2)
        self.broker = h.helicsCreateBroker("zmq", "", self.initstring)
        h.helicsBrokerSetTimeBarrier(self.broker, 0.0)
        print("Initialized broker")
        time.sleep(2)

        graph_dict = self.broker.query("broker", "data_flow_graph")
        self.broker.disconnect()
        return get_inputs_outputs(graph_dict)
