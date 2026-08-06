---
title: 5-minute quickstart
description: Install the OEDISI web app and run your first simulation.
---

# 5-minute quickstart

This quickstart gets the OEDISI web app running and executes a ready-made simulation
**template** end-to-end. You will run the *sample feeder* scenario used throughout the
Beginner track: an [OpenDSS](https://www.epri.com/pages/sa/opendss) distribution feeder
feeding a **measurement** federate and a **state estimator**, with the results captured
by a **recorder**.

:::{tip} Prefer the full setup?
This page uses the shortest path. For per-repository details, prerequisites, and
version notes, see **[Install everything](install.md)**.
:::

## 1. Get the code

```bash
git clone https://github.com/openEDI/oedisi-frontend-app.git
git clone https://github.com/openEDI/oedisi-components.git
cd oedisi-components && git submodule update --init --recursive && cd ..
```

## 2. Point the app at the components

The backend resolves components through the `OEDISI_COMPONENTS` environment variable,
which must point at the `Components/` directory of `oedisi-components`:

```bash
export OEDISI_COMPONENTS="$(pwd)/oedisi-components/Components"
```

## 3. Install and start

```bash
cd oedisi-frontend-app
npm install
uv --directory server sync
npm run dev:all
```

`npm run dev:all` starts three processes:

| Service          | URL                     | Purpose                        |
| ---------------- | ----------------------- | ------------------------------ |
| Frontend (Vite)  | <http://localhost:5173> | The web UI                     |
| Backend (FastAPI)| <http://localhost:3001> | Builds and runs simulations    |
| JupyterLab       | <http://localhost:8888> | Embedded result notebooks (full read-write access in local mode) |

## 4. Run a template

1. Open <http://localhost:5173> and go to **Saved Templates**.

:::{figure} images/ui/home.png
:alt: The OEDISI home page with cards for creating a simulation, viewing saved templates, and checking status.
:width: 100%
The OEDISI home page.
:::

2. Pick a template and click **Run**.
3. You are taken to the **run detail** page — watch the status move from
   `running` to `done` and expand the per-federate logs.

:::{important} One simulation at a time
The backend runs a single HELICS broker, so only **one** simulation can run at a time.
Cancel or wait for the current run before starting another.
:::

## 5. See the results

When the run finishes, open **Results** to plot the recorded voltages over time, or open
**Notebook** to analyze the raw data in JupyterLab.

:::{figure} images/ui/results.png
:alt: The results page plotting voltage magnitudes across buses, with a dataset selector and a time-index slider.
:width: 100%
Recorded results, ready to explore.
:::

## Next steps

- New to the UI? Take the **[guided tour](beginner/ui-tour.md)**.
- Want to understand the moving parts first? Read **[How OEDISI works](overview.md)**.
- Ready to add your own algorithm? Go to **[Build a component](intermediate/build-a-component.md)**.
