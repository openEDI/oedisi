---
title: 3. Add a subscription
description: Consume a typed input and let HELICS drive the component's clock.
---

# 3. Add a subscription

A component that only publishes is a data source. Most algorithms are not: a state
estimator needs measurements, an OPF needs a topology, a load model needs voltage. This
page builds a component that reads before it writes, which changes both its interface and
the shape of its time loop.

## Algorithm

We'll use a very basic function to take in _voltage_ and return _power_ assuming constant current.

```python
def constant_current_power(base_power, base_voltage, voltage):
    return [p * v / base_voltage for p, v in zip(base_power, voltage, strict=True)]
```

The configuration shrinks accordingly. It keeps `node_ids`, `equipment_ids`, and
`base_power` from page 1, and adds a nominal `base_voltage`.

```python
class ConstantCurrentConfig(HELICSFederateConfig):
    node_ids: list[str]
    equipment_ids: list[str]
    base_power: list[float]
    base_voltage: float = 2400.0
```

## Declare the input

Add a `dynamic_inputs` entry to
`constant_current_component/component_definition.json`:

```json
{
  "directory": "constant_current_component",
  "execute_function": "python constant_current.py",
  "static_inputs": [
    { "type": "", "port_id": "node_ids" },
    { "type": "", "port_id": "equipment_ids" },
    { "type": "", "port_id": "base_power" },
    { "type": "", "port_id": "base_voltage" }
  ],
  "dynamic_inputs": [{ "type": "VoltagesMagnitude", "port_id": "voltages" }],
  "dynamic_outputs": [{ "type": "PowersReal", "port_id": "power" }],
  "capabilities": { "broker_config": true }
}
```

The declared type,
[`VoltagesMagnitude`](../reference/data-types.md#datatype-voltagesmagnitude), is a promise
in both directions. Only a `VoltagesMagnitude` publication may be wired here, and in
exchange the code may assume that is what arrives.

:::{note} Inputs that are declared but not wired
Mark an input `"optional": true` if the component can run without it.

An unwired input is simply absent from the generated `input_mapping.json`, so optional
keys need a defensive lookup (`if "voltages" in input_mapping`).
:::

## Open the subscription

```python
with open("input_mapping.json") as f:
    input_mapping = json.load(f)

self.sub_voltages = self.fed.register_subscription(input_mapping["voltages"], "")
```

The key `"voltages"` is the declared `port_id`. The value is the publication key
`oedisi build` computed from the wiring diagram. No upstream federate name is ever
hard-coded, so the same component works wherever it is wired.

## Decode into a model

```python
voltages = VoltagesMagnitude.model_validate(self.sub_voltages.json)
by_id = dict(zip(voltages.ids, voltages.values, strict=True))
node_voltages = [by_id[node] for node in self.config.node_ids]
```

`sub.json` parses the JSON the publisher sent, and `model_validate` turns it into a typed
object, raising if a field is missing or the wrong shape. After that, every line can rely
on `voltages.values`, `voltages.ids`, and `voltages.time`.

The upstream federate decides how many buses it reports and in what order. A feeder may
publish every node in the network while the load model cares about three.
Indexing by position will silently return the wrong bus. The list of `ids` makes
a measurement self-describing.

## Wait for input changes

Our constant component asks for the end of time and lets HELICS wake it when
data arrives.

```python
self.fed.enter_executing_mode()

granted_time = self.fed.request_time(h.HELICS_TIME_MAXTIME)
while granted_time < h.HELICS_TIME_MAXTIME:
    if self.sub_voltages.is_updated():
        voltages = VoltagesMagnitude.model_validate(self.sub_voltages.json)
        by_id = dict(zip(voltages.ids, voltages.values, strict=True))

        power = PowersReal(
            values=constant_current_power(
                self.config.base_power,
                self.config.base_voltage,
                [by_id[node] for node in self.config.node_ids],
            ),
            ids=self.config.node_ids,
            equipment_ids=self.config.equipment_ids,
            time=voltages.time,
        )
        self.pub_power.publish(power.model_dump_json())

    granted_time = self.fed.request_time(h.HELICS_TIME_MAXTIME)
```

Requesting `HELICS_TIME_MAXTIME` means the federate has nothing of its own to do and
should be woken when something happens. The broker grants an earlier time whenever a
subscription updates. Once every upstream federate has disconnected there is nothing left
to wake it for, so the grant finally comes back as `MAXTIME` and the loop ends. That is
how a "reactive" federate learns the simulation is over.

`is_updated()` distinguishes a genuinely new value from being granted a time for some
other reason. Typically it is not necessary if there is only one input being read.

:::{important} Which loop shape fits which component
- **No inputs** (players, feeders, weather): step the clock with `request_time(t)` for
  each `t` the federate intends to publish at.
- **Driven by inputs** (estimators, controllers, load models, recorders): request
  `HELICS_TIME_MAXTIME` and react.
- **Both**, meaning an internal timestep plus incoming measurements: request the next
  internal time and handle being granted an earlier one.

The wrong shape is the usual cause of a federation that hangs or produces one row of
output. See
[timing configuration](https://docs.helics.org/en/latest/user-guide/fundamental_topics/timing_configuration.html).
:::

Note `time=voltages.time`. The published power is the power at the time of that voltage
measurement, so the timestamp propagates from input to output.

The complete file is
[`constant_current_component/constant_current.py`](https://github.com/openEDI/oedisi/tree/main/docs/tutorial/example/constant_current_component/constant_current.py).
Its entry point now reads both generated files:

```python
if __name__ == "__main__":
    with open("static_inputs.json") as f:
        config = ConstantCurrentConfig.model_validate(json.load(f))
    with open("input_mapping.json") as f:
        input_mapping = json.load(f)
    ConstantCurrentFederate(config, input_mapping).run()
```

## Check the interface

This component cannot run alone, since with nothing publishing voltages it would wait
forever, but its ports can still be verified:

```bash
oedisi test-description \
    --component-desc constant_current_component/component_definition.json \
    --parameters test_parameters_constant_current.json \
    --target-directory /tmp/check
```

The mock federate publishes on the input port and subscribes to the output port, so a
passing run means both sides of the interface are registered under the declared names.

:::{tip} Checkpoint
The component declares a typed input, opens whatever subscription the build step assigns
it, decodes it into a Pydantic model, looks values up by id, and reacts to data instead of
driving the clock. It still needs something to talk to.
:::

Next: **[feed it recorded data and run the whole thing](4-run-the-full-simulation.md)**.
