import time

import helics as h


def get_inputs_outputs(graph_dict):
    federate_inputs = {}
    federate_outputs = {}
    federate_id_handle2key = {}

    federate_id2name = {}
    for c in graph_dict["cores"]:
        for fed in c["federates"]:
            name = fed["attributes"]["name"]
            federate_id2name[fed["attributes"]["id"]] = name
            pub_keys = []
            for pub in fed.get("publications", []):
                federate_id_handle2key[(pub["federate"], pub["handle"])] = pub["key"]
                pub_keys.append(pub["key"])
            federate_outputs[name] = pub_keys

    for c in graph_dict["cores"]:
        for fed in c["federates"]:
            name = fed["attributes"]["name"]
            sub_keys = []
            for sub in fed.get("inputs", []):
                for source in sub["sources"]:
                    sub_keys.append(
                        federate_id_handle2key[(source["federate"], source["handle"])]
                    )
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
        # Wait until federates have hit the time barrier
        self.wait_until_connected()

        graph_dict = self.broker.query("broker", "data_flow_graph")
        self.broker.disconnect()
        return get_inputs_outputs(graph_dict)

    def wait_until_connected(self):
        print("Waiting for initialization")
        while True:
            time.sleep(2)
            current_state = self.broker.query("broker", "current_state")
            cores = current_state["cores"]
            if len(cores) == 2 and all(
                (core["state"] == "init_requested" for core in cores)
            ):
                return
