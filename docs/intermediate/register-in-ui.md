---
title: Register it in the UI
description: Make your component appear in the designer palette.
---

# Register it in the UI

Once your component builds and passes `oedisi test-description`, make it available in the
designer palette.

## 1. Put the component where OEDISI can find it

The backend resolves components through the `OEDISI_COMPONENTS` environment variable,
which points at the `Components/` directory of `oedisi-components`. Place your component
folder there (or add its repository as a submodule):

```bash
export OEDISI_COMPONENTS="/path/to/oedisi-components/Components"
ls "$OEDISI_COMPONENTS/my_component/component_definition.json"
```

## 2. Add it to the registry

The web app reads `oedisi-frontend-app/server/components.json` — a map from the **display
name** shown in the palette to the component's definition file:

```json
{
  "Recorder": "${OEDISI_COMPONENTS}/recorder/component_definition.json",
  "MyComponent": "${OEDISI_COMPONENTS}/my_component/component_definition.json"
}
```

The key is the palette label; it can differ from the folder name (for example
`StateEstimatorComponent` maps to the `wls_federate` folder). The `${OEDISI_COMPONENTS}`
placeholder is expanded by the backend at startup.

## 3. Restart and refresh

Restart the backend (or `npm run dev:all`) so it re-reads the registry. Your component now
appears in the designer's **Components** palette, typed by the ports you declared in
`component_definition.json`.

:::{seealso}
The [component catalog](../reference/component-catalog.md) is generated from exactly this
registry — once registered, your component belongs there too.
:::

## Next step

**[Run your simulation](run-your-simulation.md)** with the new component wired in.
