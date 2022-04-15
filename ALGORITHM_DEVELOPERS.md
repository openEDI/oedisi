# Algorithm Description

Each algorithm needs a `component_definition.json` such as in
`test/test_basic_system/test_component_type/component_definition.json`. If this
is not sufficient, a Python class can be created for more complex
initializations.

For available types, see the `types` folder.

# Algorithm Implementation

- *Static inputs* will be provided in a `static_inputs.json` dictionary.
The `name` input *must* be used to define the HELICS federate name.

- Dynamic inputs can either be a subscription or an endpoint target,
with subscriptions being preferred.

An `input_mapping.json` file is a dictionary with keys given by the names in the
static inputs of`component_definition.json`. The outputs will be names. You
*must* open subscriptions or use the endpoint target with the corresponding
name.

- Dynamic outputs can either be a publication or an endpoint. The name *must* be
prefaced by the federate name and a '/'. This can be automatically done by
setting up a non-global publication or endpoint.

# Using the types

Each type should use either pub/sub or endpoints for now. Future HELICS develops
may make translation between the two possible.

Data should be transferred using the JSON schema described in `types`.
