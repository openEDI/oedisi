Design
======

The framework takes a list of components and links between them.
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
3. For each link, find the appropriate key name ({federate_name}.{output_name}).
4. Configure the component with the mapping functions.
5. Collect all the execution functions into the full runner JSON.
6. Generate a shell script running the JSON.


Improvements
============

- Better Type Checking
- A type library with some Python utilities with JSON schema export
- Programmatic interface to wiring diagram (with an eye towards compatibility with Eclipse ELK)
