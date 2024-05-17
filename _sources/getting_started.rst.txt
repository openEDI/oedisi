Getting Started
===============

This guide should walk through installation and running one of the basic
simulations.

Installation
------------

The primary dependencies for the library are:
1. `helics`
2. `helics-apps`
3. `pydantic`

To run any simulation, you need the `helics-cli`.

These can be installed using pip

.. code-block:: bash

    pip install helics==3.1.2.post7
    pip install helics-apps==3.1.0
    pip install git+https://github.com/GMLC-TDC/helics-cli.git@main
    pip install pydantic


We can then install the library using `setup.py`.

.. code-block:: bash

   python setup.py install

You can also use `python setup.py develop` which allows for better uninstalling
and changes.

The Algorithm: Component Description
------------------------------------

In the `tests/test_basic_system/test_component_type` directory, we can see a very basic component and
component description with all the elements necessary for a simulation.

.. code-block:: json

   {
        "directory": "test_component_type",
        "execute_function": "python test_component_type.py",
        "static_inputs": [],
        "dynamic_inputs": [
            {"type": "", "port_id": "test1"}
        ],
        "dynamic_outputs": [
            {"type": "", "port_id": "test2"}
        ]
    }

The *federate name* will be given in the static inputs under the key "name".

Each `dynamic_output` should be published under the `federate_name/port_name`.

For each input, the federate should register a subscription by finding
the corresponding value in a dictionary in a `input_mapping.json`.


Wiring Diagram Configuration
----------------------------

The last piece of JSON configuration is the "wiring diagram" which
describes all the components in your current simulation, as well as
the links between them.

A basic example exists under `test/test_basic_system/test_basic_system.json`.

We can see how each component has a name, type, and set of static parameters.

Each link goes from a source component and port to a target component and port.

.. code-block:: json

    {
        "name": "basic_system",
        "components": [
            {
                "name": "basic_component1",
                "type": "TestComponent",
                "parameters": {}
            },
            {
                "name": "mock_component1",
                "type": "MockComponent",
                "parameters": {
                    "inputs": ["sub1"],
                    "outputs": {}
                }
            }
        ],
        "links": [
            {
                "source": "basic_component1",
                "source_port": "test2",
                "target": "mock_component1",
                "target_port": "sub1"
            }
        ]
    }



Compiling into HELICS CLI Runner Configuration
----------------------------------------------

To compile a simulation, we have to load all the components in,
as well as the wiring diagram. At this stage, we can also
load in components whose initialization is more complicated.
In this simulation, the `MockComponent`'s dynamic outputs and inputs
can depend on the initial parameters.

Then we can `generate_runner_config`
and create a configuration the HELICS CLI can read. This will
also copy over all the components into directories with those component names.

This is saved at `test_system_runner.json`.

.. code-block:: python

    from oedisi.componentframework.basic_component import component_from_json
    from oedisi.componentframework.system_configuration import (
        generate_runner_config,
        WiringDiagram,
    )
    from oedisi.componentframework.mock_component import MockComponent


    def bad_type_checker(type, x):
        return True


    TestComponent = component_from_json(
        "test_component_type/component_definition.json", bad_type_checker
    )
    component_types = {"TestComponent": TestComponent, "MockComponent": MockComponent}

    wiring_diagram = WiringDiagram.parse_file("test_basic_system.json")
    runner_config = generate_runner_config(wiring_diagram, component_types)

    with open("test_system_runner.json", "w") as f:
        f.write(runner_config.json(indent=2))

Running the simulation
----------------------

Assuming you have the helics-cli package in your path:

.. code-block:: bash

   helics run --path=test_system_runner.json

Troubleshooting
---------------

If the simulation fails, you may **need** to kill the `helics_broker` manually before you can start a new simulation.

When debugging, you should check the `.log` files for errors. Error code `-9` usually occurs when it is killed by the broker as opposed to failing.

Results
-------

For each component, there will be a directory with any files you save.

In addition, the helics-cli run command will pipe all output into `{component_name}.log` files.
