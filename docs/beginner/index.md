---
title: Beginner — use the UI
description: Run existing simulations and read results from the web app, no code required.
---

# Beginner — use the UI

This track is for **users** who want to run power-system co-simulations without writing
code. You will work entirely in the OEDI-SI web app: browse ready-made components, run
saved templates, and analyze results.

## What you'll learn

1. **[A tour of the UI](ui-tour.md)** — every screen, from the designer canvas to the
   results plots and embedded notebooks.
2. **[Run a template](run-a-template.md)** — load a ready-made simulation, launch it,
   watch it run, and read the output.
3. **[Analyze results in a notebook](analyze-results.ipynb)** — an executable notebook
   that loads recorded data and plots it.

To see all available components, visit the **[Component catalog](../reference/component-catalog.md)**
in the Reference section.

## Before you start

Make sure the app is running (`npm run dev:all`) and reachable at
<http://localhost:5173>. If not, follow the **[quickstart](quickstart.md)** or the full
**[install guide](install.md)** first.

:::{note} Notebook access modes
When running locally (`npm run dev:all`), you have full read-write access to Jupyter
notebooks for analyzing results. In cloud or server deployments, notebooks are served
**read-only** via Voilà for security reasons — you can view and execute cells but cannot
save changes.
:::

:::{tip}
If you are curious *how* the UI turns your diagram into a running simulation, read
**[How OEDI-SI works](overview.md)** — but it is not required for this track.
:::
