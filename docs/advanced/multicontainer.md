---
title: Multi-container
description: Run each component in its own container over a REST contract.
---

# Multi-container

# Multi-container

For isolation and distribution, OEDISI can run **each component in its own container**.
Instead of local processes coordinated by a local broker, the components talk to an
orchestrator over a small **REST contract** while HELICS still handles the co-simulation
messaging between them.

## The REST contract

Every containerized component exposes the three endpoints from
[Build a component](../intermediate/build-a-component.md):

| Method & path | Purpose |
| --- | --- |
| `GET /` | Health check — returns the container's hostname and IP. |
| `POST /configure` | Receive a `ComponentStruct`; write `input_mapping.json` + `static_inputs.json`. |
| `POST /run` | Receive a `BrokerConfig`; launch the federate. |

## 1. Add hosts and ports to the wiring diagram

In multi-container mode each [`Component`](api.md#api-component) needs a `host` and a
`container_port` so the orchestrator can reach it:

```json
{
  "name": "feeder",
  "type": "LocalFeeder",
  "host": "feeder",
  "container_port": 5678,
  "parameters": { "feeder_file": "..." }
}
```

## 2. Build the container artifacts

Pass `-m/--multi-container` to `oedisi build`. Instead of a single `system_runner.json`,
it generates per-component Dockerfiles, a `docker-compose.yml`, and Kubernetes manifests:

```bash
oedisi build -m --system scenario.json --component-dict components.json
```

See [`oedisi build`](cli.md#cli-build) for all options (target directory, broker port,
simulation id).

## 3. Launch

Run the generated system with either backend:

```bash
oedisi run-mc --runner build/docker-compose.yml -d   # Docker Compose
oedisi run-mc --runner build/kubernetes -k           # Kubernetes
```

`oedisi run-mc` prunes stale Docker systems/networks first, then brings the containers up.
See [`oedisi run-mc`](cli.md#cli-run-mc).

:::{warning} Apple Silicon
On M1/M2/M3 Macs, force the image platform so multi-arch base images resolve:

```bash
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```
:::

## How it fits together

```{mermaid}
flowchart LR
  subgraph Orchestrator
    B[("HELICS broker")]
  end
  B <-->|HELICS| F1["feeder<br/>container :5678"]
  B <-->|HELICS| F2["estimator<br/>container :5683"]
  B <-->|HELICS| F3["recorder<br/>container :5679"]
  O["oedisi run-mc"] -.->|configure and run| F1
  O -.-> F2
  O -.-> F3
```

The wiring diagram and [data types](data-types.md) are identical to the single-container
path — only packaging and transport change.
