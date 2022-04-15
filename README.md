# Component Framework: SGIDAL-testing Framework

The component framework's primary purpose is to instantiate new components with the right HELICS settings in a running simulation.

## Documentation

See [docs/index.rst](docs/index.rst).

There's also a [getting started guide](docs/getting_started.rst) with a very basic example.

## Example

The repository [`sgidal-example`](https://github.com/openEDI/sgidal-example/) contains a basic example including
- OpenDSS federate
- measuring federate
- weighted least squares state estimator federate
- recording federates

## Dependencies

- `helics-apps` version >= 3.1.0 
- `helics` version >= 3.1.0 (latest at present is 3.1.2post7)
- `pydantic`
