---
title: A tour of the UI
description: Every screen of the OEDISI web app, in the order you'll use them.
---

# A tour of the UI

# A tour of the UI

This tour walks through every screen of the OEDISI web app in the order you'll use
them, from the landing page to the analysis notebook. The screenshots use the built-in
**NLR DSSE IEEE 123** example — an IEEE 123-bus feeder feeding a measurement layer and a
weighted-least-squares state estimator, with recorders capturing the results.

:::{tip}
Make sure the app is running (`npm run dev:all`) and open <http://localhost:5173>. If it
isn't, see the **[quickstart](../quickstart.md)** or **[install guide](../install.md)**.
:::

## Home

The landing page is your hub. Each card is an entry point: create a new simulation, open
a saved one, or check simulation status.

:::{figure} ../images/ui/home.png
:alt: The OEDISI home page showing cards for creating a new simulation, viewing saved templates, and checking simulation status.
:width: 100%
The OEDISI home page.
:::

## The designer

**Start Designing** opens the flowchart designer — where a simulation is assembled. It
has three regions:

1. **Components palette** (left) — every registered component you can drag onto the
   canvas. See the full list in the **[component catalog](component-catalog.md)**.
2. **Canvas** (center) — the wiring diagram. Nodes are components; edges are typed
   connections between their ports.
3. **Properties panel** (right) — configure the selected component's inputs, or inspect a
   connection.

:::{figure} ../images/ui/designer-annotated.png
:alt: The flowchart designer with the components palette on the left (1), the canvas with a wired DSSE diagram in the center (2), and the properties panel on the right (3).
:width: 100%
The designer, showing the NLR DSSE example wired up: feeder → sensors → state estimator → recorders.
:::

You build a diagram by dragging components from the palette onto the canvas and connecting
their ports:

:::{figure} ../images/ui/designer.gif
:alt: Animation of dragging components from the palette onto the designer canvas.
:width: 100%
Drag components from the palette onto the canvas to compose a simulation.
:::

When you connect two nodes, the properties panel lets you pick which typed signal flows
along the edge (for example `VoltagesMagnitude` from the feeder to a sensor). Use **💾 Save
Template** to store your diagram.

## Saved templates

**Saved Templates** lists every simulation you've saved. Each card shows the components,
the node/connection counts, and actions: **Run**, **Load** (open in the designer),
**Notebook**, **Download JSON**, and **Delete**.

:::{figure} ../images/ui/saved-templates.png
:alt: The saved templates page listing several IEEE 123 simulation templates, each with Run, Load, Notebook, Download JSON, and Delete buttons.
:width: 100%
Saved simulation templates.
:::

## Runs

Running a template creates a **run**. The runs list is your history — each row shows the
run name, status, and timing.

:::{figure} ../images/ui/runs.png
:alt: The runs list showing simulation runs with status badges.
:width: 100%
The list of simulation runs.
:::

## Run detail

Opening a run shows its live status (`running` → `done`/`failed`), the exit code, and the
per-federate **logs**. When a run finishes, the **Results** and **Notebook** buttons
appear.

:::{note} Notebook access
The **Notebook** button opens an embedded JupyterLab environment for analyzing run results.
In cloud or server deployments, notebooks are read-only for security. Local deployments
enable full read-write access.
:::

:::{figure} ../images/ui/run-detail.png
:alt: The run detail page for the NLR DSSE IEEE 123 run, showing a Done status, exit code 0, and collapsible per-federate logs.
:width: 100%
A completed run, with per-federate logs.
:::

## Results

The results view plots the data captured by each **Recorder**. Pick a dataset, scrub
through timesteps with the slider, and optionally **compare** two datasets (for example an
estimate against the true values).

:::{figure} ../images/ui/results.png
:alt: The results page showing a plot of voltage magnitudes across buses for the recorded dataset, with a dataset selector and a time-index slider.
:width: 100%
Recorded voltage magnitudes, plotted per bus.
:::

## Analysis notebook

For deeper analysis, **Notebook** opens an embedded JupyterLab pointed at the run's output
directory. It comes pre-populated with a `DATA_DIR` and the imports you need, and you can
**Save to Template** so the analysis travels with every future run.

:::{figure} ../images/ui/notebook.png
:alt: An embedded JupyterLab notebook titled Analysis Notebook, with a cell setting DATA_DIR to the run's build directory.
:width: 100%
The embedded analysis notebook.
:::

## Next steps

- **[Run a template](run-a-template.md)** end-to-end.
- Reproduce the analysis yourself in the **[executable results notebook](analyze-results.ipynb)**.
- Browse the **[component catalog](component-catalog.md)** to see what each block does.
