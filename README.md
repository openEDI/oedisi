# Oedisi


[![Main - Integration Tests](https://github.com/openEDI/oedisi/actions/workflows/test-api.yml/badge.svg)](https://github.com/openEDI/oedisi/actions/workflows/test-api.yml)
[![Main - Unit Tests](https://github.com/openEDI/oedisi/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/openEDI/oedisi/actions/workflows/unit-tests.yml)
[![Documentation](https://github.com/openEDI/oedisi/actions/workflows/build-docs.yml/badge.svg)](https://openedi.github.io/oedisi/)
[![PyPI version](https://badge.fury.io/py/oedisi.svg)](https://badge.fury.io/py/oedisi)

`oedisi` (OpenEDI - System Integration) is an orchestration interface for HELICS power simulations.

- connects algorithms and data in a co-simulation framework HELICS by instantiating new components with the right HELICS configuration
- runs simulations (including with debug features) using the `oedisi` CLI tool.
- provides common [Pydantic](https://github.com/pydantic/pydantic) models for communications between power system algorithms and data in `oedisi.types`

## Documentation

[Main Docs](https://openedi.github.io/oedisi/)

[Getting Started](https://openedi.github.io/oedisi/getting_started.html) (with example)

## Example

The repository [`sgidal-example`](https://github.com/openEDI/sgidal-example/) contains a basic example including
- OpenDSS federate
- measuring federate
- weighted least squares state estimator federate
- recording federates