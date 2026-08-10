---
title: Install everything
description: Set up the framework, components, HELICS runtime, and web app across all three repositories.
---

# Install everything

OEDI-SI spans three repositories. This page covers a full local install of all of them.
For the shortest path to a running app, see the **[quickstart](quickstart.md)**.

## Prerequisites

| Tool             | Version   | Needed for                               |
| ---------------- | --------- | ---------------------------------------- |
| Python           | ≥ 3.10    | `oedisi`, components, backend            |
| Node.js + npm    | ≥ 18      | Frontend UI                              |
| [uv](https://docs.astral.sh/uv/) | latest | Backend dependency management |
| HELICS runtime   | ≥ 3.4     | Running simulations                     |
| Docker           | optional  | [Multi-container](advanced/multicontainer.md) runs |

## 1. The framework and CLI (`oedisi`)

```bash
pip install oedisi
oedisi --help          # verify the CLI is on your PATH
```

This installs the component framework, the `oedisi.types` data models, and the
`oedisi` command-line tool. It also pulls in the HELICS Python bindings.

## 2. The HELICS runtime

Simulations are launched with the `helics run` command and coordinated by the
`helics_broker` binary. Install both:

```bash
pip install "helics[cli]" helics-apps
helics --version       # verify
helics run --help      # verify the launcher
```

:::{note}
`helics[cli]` adds the `helics run` launcher extras; `helics-apps` provides the
`helics_broker` executable that coordinates federates.
:::

## 3. The components (`oedisi-components`)

```bash
git clone https://github.com/openEDI/oedisi-components.git
cd oedisi-components
git submodule update --init --recursive   # pulls the external algorithm components
```

Tell OEDISI where the components live by pointing `OEDISI_COMPONENTS` at the
`Components/` directory:

```bash
export OEDISI_COMPONENTS="$(pwd)/Components"
```

:::{warning} Component dependencies for local runs
When you run **locally** (not via Docker), each component executes as a local federate,
so its Python dependencies (for example `OpenDSSDirect.py` for the feeder, `scipy` for
the estimator) must be importable in your environment. Install the packages listed in
each component's `pyproject.toml`, or use the **[multi-container](advanced/multicontainer.md)**
workflow for full isolation.
:::

## 4. The web app (`oedisi-frontend-app`)

```bash
git clone https://github.com/openEDI/oedisi-frontend-app.git
cd oedisi-frontend-app
npm install
uv --directory server sync
npm run dev:all
```

Then open <http://localhost:5173>.

## Version compatibility

| Repository            | Tracks                                   |
| --------------------- | ---------------------------------------- |
| `oedisi`              | 3.x (Pydantic 2.x, HELICS ≥ 3.4)         |
| `oedisi-components`   | targets `oedisi~=3.0`                    |
| `oedisi-frontend-app` | backend depends on `oedisi` 3.x via `uv` |

:::{tip}
Keep the three repositories on compatible major versions. The component and frontend
repos both build against `oedisi` 3.x; mixing a 2.x framework with 3.x components will
fail validation.
:::

## Verify your install

```bash
oedisi --help          # framework CLI
helics run --help      # HELICS launcher
echo "$OEDISI_COMPONENTS"   # should print the Components/ path
```

With all four in place, continue to the **[UI tour](beginner/ui-tour.md)** or run the
**[quickstart](quickstart.md)** template.
