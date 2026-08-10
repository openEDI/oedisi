---
title: 4. Run the full simulation
description: Drive the component with recorded data using the Player, and check the results.
---

# 4. Run the full simulation

The constant-current component needs voltages. A feeder simulator would provide them in a
real study, but the **Player** federate is faster to iterate on: it replays a recorded file
as a stream of typed measurements.

Three federates this time, `Player` → `ConstantCurrentComponent` → `Recorder`, with our
component in the middle.

## Input data

The Player reads a CSV or Feather file whose columns are measurement `ids` plus a `time`
column, and publishes one row per timestep. `voltages.csv` holds four steps with a voltage
sag in the middle:

```text
113.1,113.2,114.1,time
2400.0,2400.0,2400.0,2017-01-01 00:00:00
2352.0,2352.0,2352.0,2017-01-01 00:15:00
2280.0,2280.0,2280.0,2017-01-01 00:30:00
2376.0,2376.0,2376.0,2017-01-01 00:45:00
```

The columns are the node ids our component looks up.

:::{note} Recorder output feeds the Player
This is the same shape the recorder wrote on page 2, so a run can be recorded once and
replayed as often as needed without rerunning the feeder.
:::

## Wire three components

Add the remaining types to `components.json`:

```json
{
  "PowerComponent": "power_component/component_definition.json",
  "ConstantCurrentComponent": "constant_current_component/component_definition.json",
  "Recorder": "Components/recorder/component_definition.json",
  "Player": "Components/player/component_definition.json"
}
```

Then `system_constant_current.json`:

```json
{
  "name": "tutorial_constant_current",
  "components": [
    {
      "name": "voltage_player",
      "type": "Player",
      "parameters": {
        "filename": "../../voltages.csv",
        "data_type": "VoltagesMagnitude",
        "number_of_timesteps": 4,
        "start_time_index": 0
      }
    },
    {
      "name": "constant_current_load",
      "type": "ConstantCurrentComponent",
      "parameters": {
        "node_ids": ["113.1", "113.2", "114.1"],
        "equipment_ids": ["Load.load1", "Load.load1", "Load.load2"],
        "base_power": [10.0, 12.5, 7.5],
        "base_voltage": 2400.0
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
      "source": "voltage_player",
      "source_port": "publication",
      "target": "constant_current_load",
      "target_port": "voltages"
    },
    {
      "source": "constant_current_load",
      "source_port": "power",
      "target": "power_recorder",
      "target_port": "subscription"
    }
  ]
}
```

`data_type` tells the Player which model to build from each row, and it MUST match the
type declared on the receiving port. A mismatch is not always loud, since Pydantic ignores
extra fields.

`filename` is read from the Player's own build directory, `build_current/voltage_player/`,
so two levels up is our tutorial directory. An absolute path works too.

## Build and run

```bash
oedisi build --system system_constant_current.json --component-dict components.json \
    --target-directory build_current
oedisi run --runner build_current/system_runner.json
```

`build_current/constant_current_load.log` shows our component waking on each new voltage:

```text
t=0.01 published [10.0, 12.5, 7.5] kW at 2017-01-01 00:00:00
t=1.0 published [9.8, 12.25, 7.35] kW at 2017-01-01 00:15:00
t=2.0 published [9.5, 11.875, 7.125] kW at 2017-01-01 00:30:00
t=3.0 published [9.9, 12.375, 7.425] kW at 2017-01-01 00:45:00
```

The HELICS times are whenever the Player published. The measurement times came in with the
voltages.

## Results

```bash
cat build_current/power_recorder/power.csv
```

```text
113.1,113.2,114.1,time
10.0,12.5,7.5,2017-01-01 00:00:00.000000
9.8,12.25,7.35,2017-01-01 00:15:00.000000
9.5,11.875,7.125,2017-01-01 00:30:00.000000
9.9,12.375,7.425,2017-01-01 00:45:00.000000
```

At 00:15 the voltage is 2352 V against a nominal 2400 V, so `113.1` draws 98% of its 10 kW
base power. Four rows in, four rows out, with timestamps preserved end to end.

For longer runs, read the Feather file instead:

```python
import pandas as pd

df = pd.read_feather("build_current/power_recorder/power.feather")
df["time"] = pd.to_datetime(df["time"])
df.set_index("time").plot()
```

:::{tip} Checkpoint
Two components written, and a three-federate co-simulation where our algorithm consumes
typed data from a federate we did not write and hands typed data to another.
:::

## Where to go next

- **[Register it in the UI](../intermediate/register-in-ui.md)** so it appears in the designer.
- **Use multicontainer**: Add the FastAPI `server.py` with `/`, `/configure`, and `/run`
  for Docker and Kubernetes. See
  **[Build a component](../intermediate/build-a-component.md)** and
  **[Multi-container](../advanced/multicontainer.md)**.

:::{seealso} Common failures
- **The run hangs at startup.** A stale `helics_broker`, or a federate that died before
  `enter_executing_mode`. Check each `build_*/<name>.log`, then `pkill helics_broker`.
- **The recorder writes nothing.** Nothing was published on the key it subscribed to.
  Compare `input_mapping.json` against the publishing federate's log.
- **`ValidationError` on startup.** A parameter in the wiring diagram does not match the
  config model, or a required field is missing.
- **`ValidationError` mid-run.** The payload is not the declared type, usually from a link
  to the wrong port or a Player with the wrong `data_type`.

More in **[Troubleshooting](../troubleshooting.md)**.
:::
