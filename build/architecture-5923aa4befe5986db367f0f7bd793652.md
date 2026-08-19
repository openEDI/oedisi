---
title: Architecture
description: How a wiring diagram becomes a running HELICS co-simulation.
---

# Architecture

OEDI-SI compiles a **wiring diagram** into a HELICS **runner config** and executes it.
This page follows that pipeline through the code in
`oedisi.componentframework.system_configuration`.

## The build pipeline

```{mermaid}
flowchart TD
  WD["WiringDiagram<br/>(components + links)"] --> IF["initialize_federates()"]
  IF -->|instantiate each component| CT["ComponentType instances"]
  IF -->|validate link compatibility| CT
  IF -->|write input_mapping.json| CT
  CT --> GRC["generate_runner_config()"]
  GRC -->|+ broker federate| RC["RunnerConfig<br/>(list of Federate)"]
  RC -->|serialize| JSON["system_runner.json"]
  JSON -->|helics run| SIM["HELICS co-simulation"]
```

## Wiring diagram

A [`WiringDiagram`](api.md#api-wiringdiagram) is the whole system: a list of
[`Component`](api.md#api-component) instances and a list of [`Link`](api.md#api-link)s.
Each component has a `name`, a `type` (which definition to use), and `parameters`; each
link connects a `source`/`source_port` to a `target`/`target_port`. Validators enforce
unique component names and that every link references real ports.

## Compiling to a runner config

[`generate_runner_config()`](api.md#api-generate-runner-config) turns a wiring diagram plus
a dictionary of component types into a [`RunnerConfig`](api.md#api-runnerconfig):

1. [`initialize_federates()`](api.md#api-initialize-federates) instantiates each component
   as a `ComponentType`, checks that linked ports are compatible, and asks each component
   to write its `input_mapping.json` (which upstream port feeds each input).
2. Each component becomes a [`Federate`](api.md#api-federate) — a `directory`, a `name`, a
   `hostname`, and an `exec` command string.
3. A **broker** federate is appended: `helics_broker -f <n> --loglevel=warning`, where
   `n` is the federate count.

The result serializes to `system_runner.json`, the file HELICS actually runs.

## Executing

`helics run --path=system_runner.json` launches the broker and every federate. Each
federate connects to the broker, registers its publications and subscriptions, and
advances through simulated time together. The `oedisi run` command wraps this; see the
[CLI reference](cli.md#cli-run).

## Single-container vs. multi-container

The pipeline above is the **single-container** path: every federate runs as a local
process. In the **[multi-container](multicontainer.md)** path, `generate_runner_config` is
replaced by generated Docker/Kubernetes artifacts, and federates coordinate over a REST
contract instead of local processes — but the wiring diagram and data types are identical.

## Where the UI fits

The web app's backend calls this same machinery: it converts a saved template to a
`WiringDiagram`, calls `generate_runner_config()`, and runs `helics run`. See
[How OEDI-SI works](../overview.md) for the end-to-end view.
