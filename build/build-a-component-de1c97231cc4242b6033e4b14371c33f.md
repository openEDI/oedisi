---
title: Build a component
description: Create a HELICS component with the required files and interface.
---

# Build a component

:::{tip} Looking for a walkthrough?
For a simpler step-by-step build of a component and simulation, follow the
**[Tutorial](../tutorial/index.md)** instead.
:::

An OEDI-SI component is a **HELICS federate** wrapped in a small **FastAPI server**. The
server exposes three standard endpoints so OEDI-SI (and the multi-container orchestrator)
can configure and launch it; the federate does the actual simulation work by subscribing
to and publishing typed values each timestep.

This page walks through the anatomy using the real `measuring_federate` and `recorder`
components as references. The canonical structure reference is
[`docs/component-structure.md`](https://github.com/openEDI/oedisi-components/blob/main/docs/component-structure.md)
in the components repo.

## Directory layout

Every component is an installable Python package in `src`-layout:

```text
my_component/
├── component_definition.json   # interface contract (ports + config)
├── Dockerfile                  # container image
├── pyproject.toml              # package metadata + dependencies
├── README.md
└── src/
    └── my_component/
        ├── __init__.py
        ├── server.py           # FastAPI app: /, /configure, /run
        └── my_federate.py      # HELICS federate logic
```

## 1. Declare the interface — `component_definition.json`

This file is the contract: the configuration the component reads once
(`static_inputs`), the values it subscribes to (`dynamic_inputs`), and the values it
publishes (`dynamic_outputs`). Each port has a `type` — one of the
[OEDI-SI data types](../reference/data-types.md) — and a `port_id`.

```json
{
  "directory": "my_component",
  "execute_function": "python -m my_component.my_federate",
  "static_inputs": [{ "type": "", "port_id": "name" }],
  "dynamic_inputs": [{ "type": "MeasurementArray", "port_id": "subscription" }],
  "dynamic_outputs": [{ "type": "MeasurementArray", "port_id": "publication" }]
}
```

:::{tip}
Use `"type": ""` for untyped configuration (file names, dates). Add `"optional": true`
to a `dynamic_input` if the simulation may run without it being wired.
:::

## 2. Expose the server — `server.py`

Every component implements the same three endpoints. This is the real pattern from
[`measuring_federate/server.py`](https://github.com/openEDI/oedisi-components/blob/main/Components/measuring_federate/src/measuring_federate/server.py):

```python
import json, os, socket
import uvicorn
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from oedisi.componentframework.system_configuration import ComponentStruct
from oedisi.types.common import BrokerConfig, DefaultFileNames, HealthCheck, ServerReply

from .my_federate import run_simulator

app = FastAPI()

@app.get("/")
async def read_root():
    """Health check — reports the container's hostname and IP."""
    hostname = socket.gethostname()
    try:
        host_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        host_ip = "127.0.0.1"
    return JSONResponse(HealthCheck(hostname=hostname, host_ip=host_ip).model_dump(), 200)

@app.post("/configure")
async def configure(component_struct: ComponentStruct):
    """Write input_mapping.json and static_inputs.json from the wiring diagram."""
    component = component_struct.component
    params = component.parameters
    params["name"] = component.name
    links = {link.target_port: f"{link.source}/{link.source_port}"
             for link in component_struct.links}
    json.dump(links, open(DefaultFileNames.INPUT_MAPPING.value, "w"))
    json.dump(params, open(DefaultFileNames.STATIC_INPUTS.value, "w"))
    return JSONResponse(ServerReply(detail="Configuration updated.").model_dump(), 200)

@app.post("/run")
async def run_model(broker_config: BrokerConfig, background_tasks: BackgroundTasks):
    """Launch the federate in the background."""
    background_tasks.add_task(run_simulator, broker_config)
    return JSONResponse(ServerReply(detail="Task started.").model_dump(), 200)

def main():
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5700")))

if __name__ == "__main__":
    main()
```

- **`/configure`** receives a `ComponentStruct` (the component instance plus
  its links) and writes `input_mapping.json` (which upstream port feeds each input) and
  `static_inputs.json` (the parameters). The standard file names live in
  `oedisi.types.common.DefaultFileNames`.
- **`/run`** receives a `BrokerConfig` (where the HELICS broker is) and starts the
  federate as a background task.

## 3. Do the work — the HELICS federate

The federate creates a value federate, registers its subscriptions and publications from
`input_mapping.json`, then advances through time. This mirrors
[`measuring_federate.py`](https://github.com/openEDI/oedisi-components/blob/main/Components/measuring_federate/src/measuring_federate/measuring_federate.py):

```python
import helics as h
from oedisi.types.common import BrokerConfig
from oedisi.types.data_types import MeasurementArray

def run_simulator(broker_config: BrokerConfig):
    # 1. Describe and connect the federate to the broker.
    fedinfo = h.helicsCreateFederateInfo()
    fedinfo.core_name = "my_component"
    fedinfo.core_type = h.HELICS_CORE_TYPE_ZMQ
    fedinfo.core_init = "--federates=1"
    h.helicsFederateInfoSetBroker(fedinfo, broker_config.broker_ip)
    h.helicsFederateInfoSetBrokerPort(fedinfo, broker_config.broker_port)
    vfed = h.helicsCreateValueFederate("my_component", fedinfo)

    # 2. Register I/O. Subscriptions come from input_mapping.json.
    import json
    input_mapping = json.load(open("input_mapping.json"))
    sub = vfed.register_subscription(input_mapping["subscription"], "")
    pub = vfed.register_publication("publication", h.HELICS_DATA_TYPE_STRING, "")

    # 3. Step through time until the simulation ends.
    vfed.enter_executing_mode()
    granted_time = h.helicsFederateRequestTime(vfed, h.HELICS_TIME_MAXTIME)
    while granted_time < h.HELICS_TIME_MAXTIME:
        measurement = MeasurementArray.model_validate(sub.json)   # read typed input
        # ... transform measurement ...
        pub.publish(measurement.model_dump_json())                # publish typed output
        granted_time = h.helicsFederateRequestTime(vfed, h.HELICS_TIME_MAXTIME)

    vfed.disconnect()
```

The key ideas:

- Subscriptions are keyed by `input_mapping.json`, which `/configure` wrote from the
  wiring diagram's links.
- Values are exchanged as JSON-serialized [OEDI-SI data types](../reference/data-types.md),
  so `sub.json` parses straight into a Pydantic model with `model_validate`.
- `helicsFederateRequestTime` drives the co-simulation clock until `HELICS_TIME_MAXTIME`.

## 4. Package it — `pyproject.toml` and `Dockerfile`

Use a `src`-layout package that depends on `helics`, `fastapi`, `uvicorn`, and `oedisi`,
and expose a console script:

```toml
[project]
name = "my-component"
dependencies = ["helics>=3.4", "fastapi", "uvicorn", "oedisi~=3.0"]

[project.scripts]
my-component-server = "my_component.server:main"

[tool.setuptools.packages.find]
where = ["src"]
```

The Dockerfile follows the shared pattern (Python 3.10 slim, `pip install -e .`, `EXPOSE`
a unique port, `CMD ["python", "-m", "my_component.server"]`).

## 5. Test the interface

Before wiring it into a system, validate that your component initializes and exposes the
ports you declared:

```bash
oedisi test-description --component-desc my_component/component_definition.json
```

See [`oedisi test-description`](../reference/cli.md#cli-test-description) for details.

## Next step

Make it show up in the app: **[register it in the UI](register-in-ui.md)**.
