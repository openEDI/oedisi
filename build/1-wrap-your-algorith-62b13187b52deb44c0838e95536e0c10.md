---
title: 1. Wrap your algorithm in a federate
description: Give a plain Python function a HELICS clock and a typed output.
---

# 1. Wrap your algorithm in a federate

We start from a function, and we'll turn it into a HELICS federate
communicating `oedisi` types.

```python
def scale_power(base_power: list[float], multiplier: float) -> list[float]:
    """Scale each real power value (kW) by a static multiplier."""
    return [multiplier * p for p in base_power]
```

## Vocabulary

A co-simulation is several independent processes advancing a shared clock together.
HELICS is the library that makes that work; these are the words it uses.

| Term | Meaning |
| ---- | ------- |
| [**Federate**](https://docs.helics.org/en/latest/user-guide/fundamental_topics/federates.html) | One simulator in the co-simulation. A component is a federate. |
| **Broker** | HELICS process that connects federates and decides when each may advance. |
| [**Publication / subscription**](https://docs.helics.org/en/latest/user-guide/fundamental_topics/value_federates.html) | How federates exchange values. A publication has a key; subscribers name that key. |
| [**Time request / grant**](https://docs.helics.org/en/latest/user-guide/fundamental_topics/timing_configuration.html) | A federate *asks* to move to a time and blocks until the broker *grants* it, possibly an earlier time than requested. |

**A federate never controls the clock by itself.** Each federate asks for a time, blocks,
then is granted the next relevant simulation time by the broker.

## Structure

1. **Algorithm**: standalone python function.
2. **Configuration**: a Pydantic model of every parameter read at startup.
3. **HELICS Federate**: the HELICS wrapper that owns time and I/O and calls the algorithm.

## Configuration

At startup a component reads `static_inputs.json` from its working directory. It holds two
kinds of keys: HELICS settings (what to name the federate, where the broker is) and the
component's own parameters. The `oedisi` base class [`HELICSFederateConfig`](../reference/api.md#api-helicsfederateconfig)
has all the HELICS configuration (name, broker info) baked in:

```python
from datetime import datetime

from oedisi.types import HELICSFederateConfig


class PowerComponentConfig(HELICSFederateConfig):
    node_ids: list[str]
    equipment_ids: list[str]
    base_power: list[float]
    multiplier: float = 1.0
    number_of_timesteps: int = 4
    step_size_seconds: float = 900.0
    start_time: datetime = datetime(2017, 1, 1)
```

[Pydantic](https://docs.pydantic.dev) models are classes whose annotations are enforced at
runtime. `PowerComponentConfig.model_validate(some_dict)` either returns an object with the
declared types or raises a `ValidationError` naming the offending field. This is safer than
a dict and more convenient than a regular class.

The `name` field for the HELICS Federate name is inherited from `HELICSFederateConfig`,
which is set by `oedisi`.

## HELICS Federate

### Create it

```python
import helics as h

fedinfo = h.helicsCreateFederateInfo()
config.apply_to_federate_info(fedinfo)  # HELICSFederateConfig
self.fed = h.helicsCreateValueFederate(config.name, fedinfo)
```

`apply_to_federate_info` copies the HELICS keys out of the config onto the HELICS info
object. That is the reason to subclass `HELICSFederateConfig` rather than write a separate
settings class.

A [*value federate*](https://docs.helics.org/en/latest/user-guide/fundamental_topics/value_federates.html)
exchanges values, as opposed to a
[message federate](https://docs.helics.org/en/latest/user-guide/fundamental_topics/message_federates.html)
that exchanges addressed packets. OEDISI components are almost always value federates.

### Register the publication

```python
self.pub_power = self.fed.register_publication("power", h.HELICS_DATA_TYPE_STRING, "")
```

`register_publication` is HELICS's **non-global** form, so HELICS prefixes the name with the
federate name and the key others see is `<federate name>/power`. OEDISI depends on exactly
this: it fills in subscription keys as `{component name}/{port id}` on downstream federates.

The payload is a string because OEDISI sends JSON instead of raw arrays.

### Publish a typed value

Rather than a bare array, publish one of the models in the
[data types reference](../reference/data-types.md). Real power at load nodes is
[`PowersReal`](../reference/data-types.md#datatype-powersreal):

```python
from oedisi.types.data_types import PowersReal

power = PowersReal(
    values=scale_power(config.base_power, config.multiplier),
    ids=["113.1", "113.2", "114.1"],
    equipment_ids=["Load.load1", "Load.load1", "Load.load2"],
    time=measurement_time,
)
self.pub_power.publish(power.model_dump_json())
```

- **`values`** - the numbers.
- **`ids`** - the *node* each value applies to. Should come from input data if possible.
- **`equipment_ids`** - the *device* each node belongs to. Several nodes share one device,
  which is why both lists exist and why they are the same length.
- **`units`** - defaulted per type (`PowersReal` is `"kW"`), so a consumer never guesses.
- **`time`** - the timestamp of the measurement, and the field most often forgotten.

:::{important}
HELICS time and measurement time are different things. HELICS time is a co-simulation
counter, here just `1, 2, 3, …`. `PowersReal.time` is the physical time the value belongs
to. It's very useful to have "real" time for results saved by the Recorder.
:::

### Step through time

Our component has no inputs, so it is a **source**: nothing will wake it up, and it must
step the clock itself.

```python
self.fed.enter_executing_mode()

for step in range(config.number_of_timesteps):
    granted_time = self.fed.request_time(step + 1)

    power = PowersReal(...)
    self.pub_power.publish(power.model_dump_json())

self.fed.disconnect()
```

`enter_executing_mode()` blocks until every federate has finished registering its
interfaces. A federation with a misconfigured broker hangs here. `request_time` then blocks
until the broker grants a time.

Requesting `step + 1` starts publishing at HELICS time 1. At time 0 a subscriber may not
yet have been granted its first step, and a value published there can be missed.

Disconnecting lets other federates race ahead safely.

:::{note}
Often times, you may want to update whenever an input changes ([page 3](3-add-a-subscription.md)),
or on some other schedule. HELICS provides many options.
:::

## Run it

The complete file is
[`power_component/power_component.py`](https://github.com/openEDI/oedisi/tree/main/docs/tutorial/example/power_component/power_component.py).
The entrypoint always reads `static_inputs.json` from the current working directory.

```python
if __name__ == "__main__":
    with open("static_inputs.json") as f:
        config = PowerComponentConfig.model_validate(json.load(f))
    PowerFederate(config).run()
```

`oedisi build` will write that file later. For now, write it by hand as
`stage1/static_inputs.json`:

```json
{
  "name": "power_component",
  "node_ids": ["113.1", "113.2", "114.1"],
  "equipment_ids": ["Load.load1", "Load.load1", "Load.load2"],
  "base_power": [10.0, 12.5, 7.5],
  "multiplier": 1.2,
  "number_of_timesteps": 4
}
```

A federation needs a broker, so start one expecting a single federate, then run the
component from the directory holding its config:

```bash
cd stage1
helics_broker -f 1 --loglevel=warning &  # Run the helics_broker in the background with 1 federate
python ../power_component/power_component.py
```

```text
t=1.0 published [12.0, 15.0, 9.0] kW at 2017-01-01 00:00:00
t=2.0 published [12.0, 15.0, 9.0] kW at 2017-01-01 00:15:00
t=3.0 published [12.0, 15.0, 9.0] kW at 2017-01-01 00:30:00
t=4.0 published [12.0, 15.0, 9.0] kW at 2017-01-01 00:45:00
```

:::{tip} Checkpoint
A federate that connects to a broker, advances through HELICS time, and publishes
`1.2 × [10, 12.5, 7.5]` as a `PowersReal` on every step, 15 minutes apart. But nothing is
listening.

If it hangs at startup, the broker is not running or expects a different number of
federates. Occasionally a stale broker can outlive a previous run, so you may need to
`pkill helics_broker`.
:::

Next: **[describe the component so `oedisi` can build it](2-describe-and-build.md)**.
