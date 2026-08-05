---
title: Advanced — API, CLI & scaling
description: Drive OEDISI from Python and the CLI, and scale out across containers.
---

# Advanced — API, CLI & scaling

This track is for engineers who want to script OEDISI, integrate it into pipelines, or
run distributed simulations.

## What you'll learn

1. **[Architecture](architecture.md)** — the component framework internals: how a wiring
   diagram becomes a runner config and a set of HELICS federates.
2. **[Command-line interface](cli.md)** — every `oedisi` command and option
   (auto-generated from the CLI itself).
3. **[Python API reference](api.md)** — the public classes and functions of the `oedisi`
   package (auto-generated from docstrings).
4. **[Data types](data-types.md)** — the `oedisi.types` Pydantic models components use to
   exchange voltages, powers, and topology.
5. **[Multi-container](multicontainer.md)** — the REST contract and the Docker Compose /
   Kubernetes workflow for distributed runs.
6. **[Deployment](deployment.md)** — hosting the docs and running the app in multi-user
   mode behind a reverse proxy.

## Prerequisites

- `oedisi` installed and on your PATH (`oedisi --help`).
- Familiarity with **[how OEDISI works](overview.md)** and, ideally, having built a
  component in the **[Intermediate track](../intermediate/index.md)**.
