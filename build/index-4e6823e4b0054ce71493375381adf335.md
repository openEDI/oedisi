---
title: Intermediate — build a component
description: Create your own HELICS component, register it in the UI, and run it.
---

# Intermediate — build a component

This track is for **developers** who want to add a new algorithm or simulator to OEDI-SI.
By the end you will have a working component that appears in the UI's palette and runs in
a simulation alongside the built-in ones.

## What you'll learn

1. **[Build a component](build-a-component.md)** — the required files, the
   `component_definition.json` interface contract, the FastAPI `server.py`, and the
   HELICS subscribe/publish loop.
2. **[Register it in the UI](register-in-ui.md)** — add your component to the frontend
   registry so it shows up in the designer palette.
3. **[Run your simulation](run-your-simulation.md)** — wire your component into a
   template, run it, and inspect the output.

## Prerequisites

- You can run the app and an existing template (the **[Beginner track](index.md)**).
- Comfort with Python and a basic understanding of publish/subscribe messaging.
- A local clone of [`oedisi-components`](https://github.com/openEDI/oedisi-components) and
  the `OEDISI_COMPONENTS` environment variable set (see **[install](install.md)**).

:::{tip} Prefer to learn by doing?
The **[Tutorial](../tutorial/index.md)** builds two components and two simulations from
scratch on the command line, explaining HELICS timing and Pydantic configuration. This
track is the shorter, UI-oriented path.
:::

:::{seealso}
The canonical component structure reference lives in the components repo:
[`docs/component-structure.md`](https://github.com/openEDI/oedisi-components/blob/main/docs/component-structure.md).
This track distills it into a hands-on walkthrough.
:::
