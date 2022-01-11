from componentframework.mock_component import MockComponent

c = MockComponent(
    "federate_name",
    {"outputs": {"pi": "double"}, "inputs": {"possible_input": "double"}},
    ".",
)

c.generate_input_mapping({})
assert c.execute_function.endswith("componentframework/mock_component.sh")
