---
title: Run your simulation
description: Wire your component into a template and run it.
---

# Run your simulation

With your component registered, use it like any built-in block.

## In the UI

1. Open the **designer** (<http://localhost:5173/designer>) and drag your component from
   the palette onto the canvas.
2. Connect its ports to upstream and downstream components. The properties panel only
   offers **type-compatible** signals, so a `MeasurementArray` output can wire only to a
   `MeasurementArray` input.
3. Set any `static_inputs` in the properties panel, then **💾 Save Template**.
4. **Run** it and inspect the output — exactly as in
   **[Run a template](../beginner/run-a-template.md)**.

## From the command line

You can also build and run a system without the UI. Given a wiring diagram (`system.json`)
and a component dictionary (`components.json`):

```bash
oedisi build --system system.json --component-dict components.json
oedisi run --runner build/system_runner.json
```

See the **[CLI reference](../advanced/cli.md)** for every option, and
**[Architecture](../advanced/architecture.md)** for what `build` produces.

## Troubleshooting

If a run fails immediately, check the component's log (on the run detail page or in
`build/<component>.log`) — a missing dependency or an unset `static_input` is the usual
cause. See **[Troubleshooting](../troubleshooting.md)**.
