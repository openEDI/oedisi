---
title: 2. Describe and build it
description: Declare the component's interface, wire it to a recorder, and run it with the CLI.
---

# 2. Describe and build it

The federate from [page 1](1-wrap-your-algorithm.md) runs, but its config was written by
hand and its broker started manually. `oedisi build` takes a "wiring diagram" JSON and
generates both.

## Interface

`component_definition.json` in our component's directory tells OEDISI its behavior.

```json
{
  "directory": "power_component",
  "execute_function": "python power_component.py",
  "static_inputs": [
    { "type": "", "port_id": "node_ids" },
    { "type": "", "port_id": "equipment_ids" },
    { "type": "", "port_id": "base_power" },
    { "type": "", "port_id": "multiplier" },
    { "type": "", "port_id": "number_of_timesteps" },
    { "type": "", "port_id": "step_size_seconds" },
    { "type": "", "port_id": "start_time" }
  ],
  "dynamic_inputs": [],
  "dynamic_outputs": [{ "type": "PowersReal", "port_id": "power" }],
  "capabilities": { "broker_config": true }
}
```

- **`execute_function`** - the command that starts the federate. It runs with the
  component's build directory as the working directory, which is how page 1's
  `open("static_inputs.json")` finds the right file.
- **`static_inputs`** - the parameters. Each `port_id` becomes a key in the generated
  `static_inputs.json`, so these names must match the fields of `PowerComponentConfig`.
  `"type": ""` means untyped: counts, dates, file names.
- **`dynamic_inputs`** - subscriptions. Empty here.
  [Page 3](3-add-a-subscription.md) has one.
- **`dynamic_outputs`** - publications. `port_id` MUST be the name passed to
  `register_publication`, and `type` names a model from the
  [data types reference](../reference/data-types.md).
- **`capabilities.broker_config`** - `true` because `PowerComponentConfig` subclasses
  `HELICSFederateConfig` and can therefore read HELICS broker settings from `static_inputs.json`.

:::{tip} Check the interface first
`oedisi test-description` starts the component against a mock federate and verifies that
the ports it registers match the ones it declares:

```bash
oedisi test-description \
    --component-desc power_component/component_definition.json \
    --parameters test_parameters_power.json \
    --target-directory /tmp/check
```

```text
Testing dynamic input names
✓
Testing dynamic output names
✓
```

`--parameters` is a file of valid `static_inputs`. It is optional, but without it the
component receives only `{"name": "component"}`. Occasionally, failed federates
can cause this test function to hang.
:::

## Component types

`oedisi build` requires a list of all components, taking the form of a
`components.json` mapping component name to a definition file:

```json
{
  "PowerComponent": "power_component/component_definition.json",
  "Recorder": "Components/recorder/component_definition.json"
}
```

Paths are relative to wherever `oedisi build` runs.

The published power needs somewhere to go. The shared component repository has a
`recorder` federate that subscribes to any measurement and writes CSV and Feather, so make
it reachable:

```bash
ln -s "$OEDISI_COMPONENTS" Components
```

## Wiring diagram

The wiring diagram lists component instances and the links between them. Create
`system_power.json`:

```json
{
  "name": "tutorial_power",
  "components": [
    {
      "name": "power",
      "type": "PowerComponent",
      "parameters": {
        "node_ids": ["113.1", "113.2", "114.1"],
        "equipment_ids": ["Load.load1", "Load.load1", "Load.load2"],
        "base_power": [10.0, 12.5, 7.5],
        "multiplier": 1.2,
        "number_of_timesteps": 4
      }
    },
    {
      "name": "power_recorder",
      "type": "Recorder",
      "parameters": {
        "feather_filename": "power.feather",
        "csv_filename": "power.csv"
      }
    }
  ],
  "links": [
    {
      "source": "power",
      "source_port": "power",
      "target": "power_recorder",
      "target_port": "subscription"
    }
  ]
}
```

Here, we give each "instance" of a component "type" (PowerComponent) a unique name.
`parameters` is combined with the HELICS information and saved to the component as `static_inputs.json`.
A link connects an output `port_id` to an input `port_id`, so the recorder can listen to our PowerComponent.

## Build

```bash
oedisi build --system system_power.json --component-dict components.json \
    --target-directory build_power
```

`build_power/` holds one directory per component: a copy of the component's code plus two
generated files.

```text
build_power/
├── power/
│   ├── power_component.py
│   ├── component_definition.json
│   ├── static_inputs.json      ← generated
│   └── input_mapping.json      ← generated
├── power_recorder/
│   └── ...
└── system_runner.json
```

`static_inputs.json` is the file written by hand on page 1:

```json
{"name": "power", "node_ids": ["113.1", "113.2", "114.1"], ...}
```

The `name` came from the component's `name` in the wiring diagram. Nothing inside the
component sets it, which is what allows one component to appear under several names in one
federation.

`input_mapping.json` names the subscriptions. The `power` component has no inputs, so its
copy is `{}`. The recorder's `input_mapping.json` is the interesting one:

```json
{"subscription": "power/power"}
```

The recorder's `subscription` port was linked to the `power` component's `power` port, so
the key is `power/power`, following the `{component name}/{port id}` convention from page
1. The recorder does not know what is upstream of it. It opens whatever key this file
names, so wiring something else into it changes only this file.

`system_runner.json` is the run plan, including a broker sized to the federation:

```json
{
  "name": "tutorial_power",
  "federates": [
    { "directory": "power", "name": "power", "exec": "python power_component.py" },
    { "directory": "power_recorder", "name": "power_recorder",
      "exec": "python -m src.recorder.record_subscription" },
    { "directory": ".", "name": "broker", "exec": "helics_broker -f 2 --loglevel=warning" }
  ]
}
```

## Run

```bash
oedisi run --runner build_power/system_runner.json
```

Each federate's output goes to `build_power/<name>.log`, and the recorder wrote its files
inside its own build directory:

```bash
cat build_power/power_recorder/power.csv
```

```text
113.1,113.2,114.1,time
12.0,15.0,9.0,2017-01-01 00:00:00.000000
12.0,15.0,9.0,2017-01-01 00:15:00.000000
12.0,15.0,9.0,2017-01-01 00:30:00.000000
12.0,15.0,9.0,2017-01-01 00:45:00.000000
```

The columns are the `ids` from the published `PowersReal`, and the `time` column is its
`time` field.

:::{warning} Relative paths resolve from the build directory
`"power.feather"` landed in `build_power/power_recorder/` because that is the federate's
working directory, not the directory `oedisi build` ran in. Every path in `parameters`
works this way, which is why [page 4](4-run-the-full-simulation.md) reads its input as
`../../voltages.csv`.
:::

:::{tip} Checkpoint
The component is declared, buildable, and connected to a federate written by someone else.
Rerunning is `oedisi build` then `oedisi run`.

If a federate exits immediately, read `build_power/<name>.log`. A `ValidationError` there
means a parameter name in the wiring diagram does not match the config model.
:::

Next: **[give the component an input](3-add-a-subscription.md)**.
