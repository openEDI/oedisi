# Component Framework: GADAL-testing Framework

[![Main - Integration Tests](https://github.com/openEDI/GADAL/actions/workflows/test-api.yml/badge.svg)](https://github.com/openEDI/GADAL/actions/workflows/test-api.yml)
[![Main - Unit Tests](https://github.com/openEDI/GADAL/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/openEDI/GADAL/actions/workflows/unit-tests.yml)
[![Documentation](https://github.com/openEDI/GADAL/actions/workflows/build-docs.yml/badge.svg)](https://openedi.github.io/GADAL/)

GADAL (Grid Algorithms and Data Analytics Library) provides a library for connecting Algorithms and Datasets in a co-simulation frameowrk. The purpose of the GADAL-testing Framework is to instantiate new components with the right HELICS settings in a running simulation.

## Documentation

[Main Docs](https://openedi.github.io/GADAL/)

[Getting Started](https://openedi.github.io/GADAL/getting_started.html) (with example)

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
