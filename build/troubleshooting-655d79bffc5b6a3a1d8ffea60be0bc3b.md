---
title: Troubleshooting & FAQ
description: Common problems running OEDI-SI and how to fix them.
---

# Troubleshooting & FAQ

## Running simulations

### Only one simulation runs at a time

OEDI-SI starts a single HELICS broker on a fixed port, so the backend permits **one active
run at a time**. If a new run is rejected, cancel the current run (the **Cancel** button
on the run detail page, or `DELETE /api/runs/{run_id}`) or wait for it to finish.

### "Address already in use" / broker port conflict

A previous simulation may have left a broker running. Find and stop stray brokers:

```bash
pgrep -fl helics_broker      # list broker processes
pkill -f helics_broker       # stop them
```

Then start your run again. You can also change the broker port with
`oedisi build --broker-port <port>`.

### A run fails immediately

Read the per-federate logs. Locally they are written next to the build output
(`build/<component>.log`); in the UI they appear in the **Logs** section of the run detail
page, and via `GET /api/runs/{run_id}/logs/{component}`. A component that exits at startup
is usually missing a Python dependency or a required `static_input`.

### `ModuleNotFoundError` from a component (local runs)

When running locally (not in Docker), each component runs in **your** Python environment,
so its dependencies must be installed. Check the component's `pyproject.toml` and install
the missing packages, or use the **[multi-container](advanced/multicontainer.md)** workflow
for isolation.

## Setup

### `OEDISI_COMPONENTS` is not set

The frontend backend resolves components through `OEDISI_COMPONENTS`, which must point at
the `Components/` directory of `oedisi-components`:

```bash
export OEDISI_COMPONENTS="/path/to/oedisi-components/Components"
```

### `oedisi: command not found`

The CLI ships with the `oedisi` package. Install it (`pip install oedisi`) and confirm the
environment's `bin` directory is on your `PATH`.

### `helics run` is missing

Install the HELICS launcher and broker: `pip install "helics[cli]" helics-apps`. Verify
with `helics run --help` and `which helics_broker`.

## Docker / multi-container

### Builds fail or hang on Apple Silicon (M1/M2/M3)

Force the image platform so multi-arch base images resolve correctly:

```bash
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

### Stale containers or networks

Prune before a fresh multi-container run so old networks don't collide:

```bash
docker system prune -f
docker network prune -f
```

## Still stuck?

- Re-read **[How OEDI-SI works](overview.md)** to confirm the mental model.
- Check the component's own `README.md` in `oedisi-components`.
- Open an issue at <https://github.com/openEDI/oedisi/issues>.
