---
title: OEDI-SI
description: Orchestration interface for HELICS power-system co-simulations.
---

# OEDI-SI

**OEDI-SI** (Open Energy Data Initiative — System Integration) is an orchestration
interface for [HELICS](https://helics.org) power-system co-simulations. It lets you
wire independent simulation **components** (feeders, state estimators, optimizers,
recorders) into a co-simulation, run them, and analyze the results — either from a
drag-and-drop **web UI** or directly from the **`oedisi` command line**.

:::{note} What OEDI-SI gives you
- A **component framework** that instantiates each algorithm as a HELICS federate with
  the correct publications, subscriptions, and configuration.
- A **web application** to assemble, run, and visualize simulations without writing code.
- Shared [Pydantic](https://docs.pydantic.dev) data models (`oedisi.types`) so components
  exchange voltages, powers, and topology in a common language.
- A **CLI** and **multi-container** workflow for reproducible and distributed runs.
:::

## Choose your path

::::{grid} 1 1 2 3

:::{card} 🟢 Beginner
:link: beginner/index.md
Use the web UI. Run existing templates, browse the component catalog, and read
your results — no coding required.
:::

:::{card} 🟡 Intermediate
:link: intermediate/index.md
Build your own component, register it so it appears in the UI, and run a
simulation that uses it.
:::

:::{card} 🔴 Advanced
:link: advanced/index.md
Drive OEDI-SI from the Python API and CLI, and scale out with the
multi-container (Docker / Kubernetes) workflow.
:::

::::

## In a hurry?

Jump straight to the **[5-minute quickstart](quickstart.md)** to install the app and run
your first simulation, or see **[how OEDI-SI works](overview.md)** for the mental model.

:::{seealso} Source repositories
OEDI-SI spans three repositories:
- [`oedisi`](https://github.com/openEDI/oedisi) — the framework, types, and CLI.
- [`oedisi-components`](https://github.com/openEDI/oedisi-components) — reusable HELICS components.
- [`oedisi-frontend-app`](https://github.com/openEDI/oedisi-frontend-app) — the web UI and backend.
:::
