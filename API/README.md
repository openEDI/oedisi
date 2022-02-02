# Testing Framework

We need something that can
1. Instantiate new modules with given HELICS settings
2. Be able to configure things like (1) federate names, (2) pub/subs and endpoints, (3) broker IP/port/type, (4) logging, (5) timing, and (6) iterations.
3. Run the system, check for errors, and accumulate logs.

# PyDSS
PyDSS can configure things like (1) federate names, (2) pub/subs and endpoints, (3) broker IP/port/type, (4) logging, (5) timing, and (6) iterations.

See https://github.com/NREL/PyDSS/blob/9de363d81f93e20770e30f97b694ba3bebf9aa7c/PyDSS/helics_interface.py and https://github.com/NREL/PyDSS/blob/9de363d81f93e20770e30f97b694ba3bebf9aa7c/examples/external_interfaces/pydss_project/Scenarios/helics/ExportLists/Subscriptions.toml.

PyDSS does not appear to have a very well-formed mapping though, since publications are a little off. Specifically they use
a TOML mapping file to get all the right subscriptions, but they use some string formatting ('{federate_name}.{obj_X}.{obj_property}') which we obviously
have no control over.

The higher level system should know probably know all the publications and subscriptions without having the run the software. The current version of HELICS
does not allow for dynamic querying of subscriptions.

## Design

We are given a list of components and links between them.
- Each component has a unique name, component type, and any parameters needed.
- Each link has a source process with output port and a target process with input port

Each component type has
- An initialization function taking parameters and the unique name.
- A list of inputs from parameters. These must be capable of configuration later.
- A list of outputs from parameters. These should be publications with keys {federate_name}.{output_name}.
- A mapping function that lets you remap the inputs. Again after parameters
- An execution function (again after parameters).

1. Initialize each component with its parameters and names along with the component type.
2. Check that all the links and component types match up (at least their names, preferably more).
3. For each each link, find the appropriate key name ({federate_name}.{output_name}).
4. Configure the component with the mapping functions.
5. Collect all the execution functions into the full runner JSON.
6. Generate a shell script running the JSON.

# What is a unique key

Options
- Use a unique id (hash?)
- Use unique federate_id + whatever key people want. But the key must be specified in a TOML file.

# Current Systems

- Power Flow: pydss using HELICS
- Some sort of measurement apparatus (?)
- State Estimator algorithm
- Getting calculated states (?)
- Optimization algorithm


# API Feedback from National Labs

[Link to API formulation](https://app.box.com/folder/151925709259?s=ea9i5z61uqoej46ne6bd1g74snqfqo2k)

