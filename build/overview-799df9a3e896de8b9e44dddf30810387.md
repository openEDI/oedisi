---
title: How OEDI-SI works
description: The mental model — components, wiring diagrams, runners, and the HELICS broker.
---

# How OEDI-SI works

OEDI-SI turns a **wiring diagram** — a set of components and the links between their ports —
into a running [HELICS](https://helics.org) co-simulation. Understanding four concepts is
enough to use everything else in these docs.

## Core concepts

Component
: A self-contained simulator or algorithm (a *feeder*, *state estimator*, *recorder*, …).
  Each component declares its interface in a `component_definition.json` file: its
  configuration (`static_inputs`) and the typed ports it subscribes to (`dynamic_inputs`)
  and publishes (`dynamic_outputs`).

Wiring diagram
: The whole system: a list of component **instances** plus **links** that connect one
  component's output port to another's input port. In code this is the
  `WiringDiagram` model in `oedisi.componentframework.system_configuration`.

Runner config
: The compiled artifact (`system_runner.json`) that HELICS actually executes. OEDI-SI
  produces it from a wiring diagram with `generate_runner_config()`.

Broker
: The HELICS process that coordinates time and message passing between all federates.

## From UI to simulation

The web app is a friendly front-end over exactly this pipeline. A saved **template**
(Vue Flow nodes + edges) is converted to a wiring diagram, compiled to a runner config,
and launched with `helics run`.

```{mermaid}
flowchart LR
  User([You]) --> UI["Web UI<br/>(Vue + Vite · :5173)"]
  UI <-->|REST JSON| API["Backend<br/>(FastAPI · :3001)"]
  API -->|generate_runner_config| Runner[["system_runner.json"]]
  Runner -->|helics run| Broker[("HELICS broker")]
  Broker --- F1["Feeder<br/>federate"]
  Broker --- F2["Estimator<br/>federate"]
  Broker --- F3["Recorder<br/>federate"]
  API -.serves.-> Jupyter["JupyterLab<br/>(:8888)"]
```

## The run lifecycle

```{mermaid}
sequenceDiagram
  actor User
  participant UI as Web UI
  participant API as Backend
  participant OEDI-SI
  participant HELICS
  User->>UI: Run a template
  UI->>API: POST /api/runs (wiring diagram)
  API->>OEDI-SI: generate_runner_config()
  API->>HELICS: helics run --path system_runner.json
  HELICS->>HELICS: orchestrate federates over time
  HELICS-->>API: federates exit, logs written
  API-->>UI: run_id + status (running → done)
  User->>UI: View results / open notebook
```

## Where each piece lives

| Concept          | Code / file                                                              |
| ---------------- | ------------------------------------------------------------------------ |
| Component        | `oedisi-components/Components/<name>/component_definition.json`           |
| Wiring diagram   | `WiringDiagram` in `oedisi.componentframework.system_configuration`      |
| Runner config    | `RunnerConfig` → `system_runner.json`                                     |
| UI template      | `oedisi-frontend-app/data/templates/*.json`                              |
| Component registry (UI) | `oedisi-frontend-app/server/components.json`                      |

Ready to see it in action? Start with the **[quickstart](quickstart.md)** or the
**[UI tour](beginner/ui-tour.md)**. Want the internals? Jump to
**[Architecture](advanced/architecture.md)**.
