---
title: Tutorial for algorithm developers
description: Turn a plain Python function into an OEDISI component and run it in a co-simulation.
---

# Tutorial for algorithm developers

This tutorial turns an algorithm into an OEDISI component that can exchange data with a
feeder simulator and with federates written by other groups. The algorithm we use is
deliberately tiny, so the only new material is the plumbing. We build two components and
run two simulations, all from the command line.

## Who this is for

The reader is comfortable with Python and numerical modelling and can already write the
algorithm they care about, but has probably not used [HELICS](https://helics.org) or
[Pydantic](https://docs.pydantic.dev), and is unsure what OEDISI adds on top of them.

HELICS moves bytes between processes and keeps their clocks aligned. OEDISI adds two
things that a federation of separately developed algorithms needs. The first is an agreed
set of typed messages, so a state estimator written at one lab can consume voltages from a
feeder written at another. The second is a declarative wiring description, so a simulation
is a JSON file rather than hand-edited config.

:::{seealso}
**[Build a component](../intermediate/build-a-component.md)** covers the same ground as
reference material, including the FastAPI `server.py` that multi-container deployments
need. This tutorial stays with the CLI.
:::

## What we build

| Stage | Artifact | New idea |
| ----- | -------- | -------- |
| **[1. Wrap your algorithm](1-wrap-your-algorithm.md)** | `PowerComponent`, publishing scaled real power on a schedule | HELICS time control, typed payloads |
| **[2. Describe and build it](2-describe-and-build.md)** | Simulation 1: `PowerComponent` → `Recorder` | `component_definition.json`, `oedisi build` |
| **[3. Add a subscription](3-add-a-subscription.md)** | `ConstantCurrentComponent`, power that responds to voltage | subscriptions, decoding typed inputs |
| **[4. Run the full simulation](4-run-the-full-simulation.md)** | Simulation 2: `Player` → `ConstantCurrentComponent` → `Recorder` | driving a component with recorded data |

## What this tutorial does not cover

- Registering the component in the web UI. See
  **[Register it in the UI](../intermediate/register-in-ui.md)**.
- The FastAPI server needed for Docker and Kubernetes deployments. See
  **[Multi-container](../advanced/multicontainer.md)**.
- Packaging, unit testing, and the code-quality bar for the shared
  **[component catalog](../reference/component-catalog.md)**.

## Prerequisites

A Python 3.10+ environment with `oedisi` and `helics` installed:

```bash
pip install oedisi
oedisi --help
```

Stages 2–4 use the `recorder` and `player` federates from the shared component
repository, so clone it and install their dependencies:

```bash
git clone https://github.com/openEDI/oedisi-components.git
cd oedisi-components && git submodule update --init --recursive && cd ..
export OEDISI_COMPONENTS="$(pwd)/oedisi-components/Components"
pip install pandas pyarrow
```

## Working files

The finished code lives in
[`docs/tutorial/example`](https://github.com/openEDI/oedisi/tree/main/docs/tutorial/example):

```text
example/
├── power_component/
│   ├── component_definition.json
│   └── power_component.py
├── constant_current_component/
│   ├── component_definition.json
│   └── constant_current.py
├── components.json                # component type -> folder
├── system_power.json              # Simulation 1 wiring diagram
└── system_constant_current.json   # Simulation 2 wiring diagram
# and some additional test and data files
```

Next: **[Wrap your algorithm in a federate](1-wrap-your-algorithm.md)**.
