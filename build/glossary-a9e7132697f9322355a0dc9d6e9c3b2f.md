---
title: Glossary
description: Key terms used across OEDI-SI and HELICS co-simulation.
---

# Glossary

:::{glossary}
HELICS
: The *Hierarchical Engine for Large-scale Infrastructure Co-Simulation*. The runtime
  that coordinates time and message passing between the independent simulators in an
  OEDI-SI system. See [helics.org](https://helics.org).

Federate
: A single participant in a HELICS co-simulation — one running component. Each federate
  advances through simulated time, publishing and subscribing to values.

Broker
: The HELICS process that connects federates, synchronizes their time, and routes
  messages. OEDI-SI adds one broker per simulation (`helics_broker`).

Component
: A reusable simulator or algorithm packaged for OEDI-SI (a feeder, estimator, recorder,
  …). Its interface is declared in `component_definition.json`.

Component definition
: The `component_definition.json` file that declares a component's `static_inputs`
  (configuration), `dynamic_inputs` (subscriptions), and `dynamic_outputs` (publications).

Wiring diagram
: The specification of a whole system: component instances plus the links between their
  ports. Represented by the `WiringDiagram` Pydantic model.

Link
: A directed connection from one component's output port (`source` / `source_port`) to
  another component's input port (`target` / `target_port`).

Port
: A named input or output on a component. Ports are typed with {term}`OEDI-SI data types`.

Publication
: A HELICS value that a federate produces each timestep — a component's `dynamic_outputs`.

Subscription
: A HELICS value that a federate consumes each timestep — a component's `dynamic_inputs`.

Runner config
: The compiled `system_runner.json` that HELICS executes, produced from a wiring diagram
  by `generate_runner_config()`. Modeled by `RunnerConfig`.

Template
: A saved simulation in the web UI — Vue Flow nodes and edges stored as JSON in
  `oedisi-frontend-app/data/templates/`. Converted to a wiring diagram when run.

Static inputs
: Configuration set once before a simulation starts (for example a feeder file name or a
  start date). Written to `static_inputs.json` for each component.

Dynamic inputs / outputs
: The typed values a component subscribes to / publishes every timestep.

OEDI-SI data types
: The Pydantic models in `oedisi.types.data_types` (for example `VoltagesMagnitude`,
  `PowersReal`, `Topology`) that give ports a shared, typed meaning. See
  [Data types](reference/data-types.md).

Feeder
: A distribution-network simulator (for example the OpenDSS-based `LocalFeeder`) that
  produces voltages, powers, and topology.

State estimation (DSSE)
: *Distribution System State Estimation* — inferring the network's electrical state from
  noisy measurements (for example the `wls_federate`).

Optimal power flow (DOPF)
: *Distribution Optimal Power Flow* — computing set-points that optimize an objective
  subject to network constraints.

Recorder
: A component that subscribes to values and writes them to disk (Feather / CSV) for
  later analysis.

Player
: A component that replays a pre-recorded dataset into a simulation.

Multi-container
: Running each component in its own Docker container, coordinated over a REST contract,
  for isolation and distribution. See [Multi-container](advanced/multicontainer.md).
:::
