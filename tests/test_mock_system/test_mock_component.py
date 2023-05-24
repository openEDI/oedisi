from oedisi.componentframework.mock_component import MockComponent
import os

if not os.path.exists("testC"):
    os.mkdir("testC")

c = MockComponent(
    "federate_name",
    {"outputs": {"pi": "double"}, "inputs": {"possible_input": "double"}},
    "testC",
)

c.generate_input_mapping({})
assert c.execute_function.endswith("componentframework/mock_component.sh")
