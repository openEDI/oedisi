``oedisi`` CLI
==============

In ``oedisi.tools``, there is a ``cli`` tool called ``oedisi``.
There are tools to build, run, and debug simulations as well
as test component description JSONs.

Occasionally, the HELICS runner will fail to start and may need
to be killed. The same may happen to the mock component used for testing.


A ``component-dict`` will be a JSON file with names to component definitions::

    {
      "ComponentOne": "component1/component_definition.json",
      "ComponentTwo": "component2/component_definition.json"
    }

Example Usage
-------------

Assuming we have our component dictionary ``components.json``,
the system JSON at ``system.json``, and we want to build to ``build``,
then most command line parameters will not be necessary.

Build and run::

    oedisi build
    oedisi run

Multi-Container REST API endpoint requirements
----------------------------------------------

+-----------------+-----------------+-----------------+-----------------+
| Endpoint        | Type            | Usage           | Reqired by      |
+=================+=================+=================+=================+
| /               | GET             | Heath check.    | All containers  |
|                 |                 | Returns         |                 |
|                 |                 | hostname and ip |                 |
+-----------------+-----------------+-----------------+-----------------+
| /profiles       | POST            | Enables upload  | Broker federate |
|                 |                 | of user defined | + simulator     |
|                 |                 | profiles to the | federate        |
|                 |                 | container       | (feeder         |
|                 |                 |                 | federate in     |
|                 |                 |                 | sigdal example) |
+-----------------+-----------------+-----------------+-----------------+
| /model          | POST            | Enables upload  | Broker federate |
|                 |                 | of user defined | + simulator     |
|                 |                 | distribution    | federate        |
|                 |                 | model to the    |                 |
|                 |                 | feeder          |                 |
|                 |                 | container.      |                 |
|                 |                 | Upload requires |                 |
|                 |                 | a zipped        |                 |
|                 |                 | distribution    |                 |
|                 |                 | model           |                 |
+-----------------+-----------------+-----------------+-----------------+
| /results        | GET             | Enables users   | Broker federate |
|                 |                 | to fetch        |                 |
|                 |                 | results from all|                 |
|                 |                 | the recorder    |                 |
|                 |                 | federates       |                 |
+-----------------+-----------------+-----------------+-----------------+
| /terminate      | GET             | Closes the      | Broker federate |
|                 |                 | HELICS library  | only            |
|                 |                 | and ternimates  | (co-simulation  |
|                 |                 | the             | orchestrator)   |
|                 |                 | co-simulation   |                 |
+-----------------+-----------------+-----------------+-----------------+
| /run            | POST            | Starts federate | All containers  |
|                 |                 | simulaton       |                 |
|                 |                 | allowing to     |                 |
|                 |                 | enter HELICS    |                 |
|                 |                 | execution mode  |                 |
+-----------------+-----------------+-----------------+-----------------+
| /sensor         | GET             | Enables         | Simulator       |
|                 |                 | retrieval of    | federate only   |
|                 |                 | available       |                 |
|                 |                 | sensors         |                 |
+-----------------+-----------------+-----------------+-----------------+
| /download       | GET             | Enables users   | Recorder        |
|                 |                 | to fetch        | federates only  |
|                 |                 | results from a  |                 |
|                 |                 | recorder        |                 |
|                 |                 | federate        |                 |
+-----------------+-----------------+-----------------+-----------------+

Multi-Container Model Setup
---------------------------

The ``oedisi`` frameworks enables users to set up models as single-container (all models running
in a single Docker container) or multi-container implementation (all componenets running in
seperate docker containers.). The framework currently supports both Docker-compose and kubernetes
configurations. By default, the  ``oedisi`` frameworks sets up the single-container simulation.
``-m`` flag can be used to build additional files needed for either Docker-compose or Kubernetes
orchestration.

Uploading user defined models requires setting the 'user_uploads_model' to true. If the flag is set to false, the model will be downloaded automatically from AWS.

Building files for multi-container implementation::

    oedisi build -m

Multi-Container Build Options
-----------------------------

The `oedisi build` command supports several options useful when creating
multi-container (Docker Compose or Kubernetes) artifacts. Use the `-m` or
`--multi-container` flag to generate the additional files needed for
orchestration.

- `--target-directory`: Directory to write the build artifacts. Default: `build`.
    Example: `oedisi build --target-directory my_build -m` will create
    `my_build/<simulation_id>/...`.
- `--system`: Path to the wiring-diagram JSON file describing the system.
    Default: `system.json`.
    Example: `oedisi build --system scenario.json -m`.
- `--component-dict`: Path to the components JSON dictionary (maps component
    types to component definition files). Default: `components.json`.
    Example: `oedisi build --component-dict components.json -m`.
- `-m, --multi-container`: Boolean flag that instructs `oedisi` to produce
    multi-container artifacts (Dockerfiles, `docker-compose.yml`, and a
    `kubernetes/` folder). Without this flag, `oedisi` builds a single-container
    `system_runner.json` used by the HELICS runner.
- `-p, --broker-port`: Port exposed by the broker service inside the
    orchestration configuration. Default: `8766`. When using Docker Compose this
    is mapped as `host:container` in `docker-compose.yml`.
- `-i, --simulation-id`: Optional identifier for the build. If omitted a
    UUID is generated and the multi-container artifacts are written to
    `<target-directory>/<simulation_id>/`. Providing a `--simulation-id` is
    useful for reproducible or repeatable builds.

Notes and requirements when using `-m`:

- Each component in the wiring diagram must include a `host` and
    `container_port` attribute; these are validated during the multi-container
    build and are required to generate networking and port mappings.
- The build will copy and slightly edit component `Dockerfile` files found in
    each component's source directory and will verify a `server.py` file exists
    for REST-enabled components.
- Output layout for a multi-container build (example):

    - `<target-directory>/<simulation_id>/docker-compose.yml`
    - `<target-directory>/<simulation_id>/kubernetes/` (service + pod/deployment files)
    - Component Dockerfiles remain in the component folders but are validated
        and used as the `build` contexts in `docker-compose.yml`.

Examples
--------

Create a multi-container build with a fixed simulation id and custom port::

        oedisi build -m --simulation-id mysim01 --broker-port 9000

Create multi-container artifacts in a custom folder using a specific system file::

        oedisi build -m --target-directory my_build --system my_system.json

Once the build process is complete, the containers can be launched by either Docker-compose
(all images will run on the local machine) or using Kubernetes (enables orchestration across multiple
machines). Navigate to the build folder and execute following command to lauch all images in the
build folder.

Running containers using Docker-compose::

    docker compose up

Stopping containers using Docker-compose::

    docker compose down

Alternately, Kubernetes setup files can be used to orchestrate the launch of all the required containers.
Kubernetes deploment files are generated within the ``kubernetes`` folder inside the build folder.
All files can be deployed using a file command (Both deployment and service files).
It is to be noted that these files can be modified to serve a unique usecases.

Running containers using Kubernetes::

    kubectl apply -f kubernetes

To access the REST API endpoint of the broker container, port forwarding can be used to expose the
container port to the local machine. The command below forwards port 8766 of the broker container
to port 8080 on the local machine.

    kubectl port-forward service/oedisi-service 8080:8766

The REST API endpoint can then be accessed at ``http://localhost:8080``

By default, the deployment file is configured to download required images from Docker Hub.
Users have to option to modify the deployment file and use a local registery (https://docs.docker.com/registry/)
to use local images instead.

Multi-Container Model Run
---------------------------

Once all required docker images are running (see last section), simulation run can be orchestration using the REST API interface.
The interface aloows users to

#. Upload private data (distribution models and associated profiles)
#. Launch the simulation
#. Retrieve simulation results

IPs for containers and corresponding exposed ports are available to users within the ``docker-compose.yml`` file in the main build folder.
To check healh of the API server the runnig container, user can open a web browser and browse to ``http://{ip}:{port}``, where ``ip``
and ``port`` are container specific (see ``docker-compose.yml``).


Identify the ``ip``  and ``port`` information for ``oedisi_broker`` container from the  ``docker-compose.yml`` file.

Upload private data
++++++++++++++++++++

#. Distribution models, compressed in ``zip`` format can be uploaded by making a POST request to the following endpoint ``http://{ip}:{port}/model``
#. Similarly, load profile, compressed in ``zip`` format can be uploaded by making a POST request to the following endpoint ``http://{ip}:{port}/profiles``

These files are automatically unzipped server side after a sucessful upload.

Launch the simulation
+++++++++++++++++++++

#. Make a POST request to the following endpoint ``http://{ip}:{port}/run`` (no payload needed for the POST request)

This starts the simulation. The Broker communicated with other container via REST API and singals them to start Helics co-simulation.

Retrieve simulation results
+++++++++++++++++++++++++++

#. Identify the ``ips``  and ``ports`` information for ``oedisi_broker`` containers from the  ``docker-compose.yml`` file.
#. Data can be downloaded by making a POST request to the following endpoint ``http://{ip}:{port}/download``. This endpoint will communicate with all participating recorder federates ans retrieve the simulation results in a single zip file,

This will later be simplified so users are able to download all results using a single endpoint fromthe broker container.




Debugging
+++++++++

If there are timing problems, it may be helpful to pause the simulation and inspect the time.
This can be done with::

    oedisi build
    oedisi run-with-pause


Output::

    ...
    Enter next time: [0.0]: 1.0
    Setting time barrier to 1.0

        Name         : comp_abc
        Granted Time : 0.0
        Send Time    : 0.0


        Name         : comp_xyz
        Granted Time : 0.0
        Send Time    : 0.0



We can debug components with ordinary debuggers and running that component in
the foreground::

    oedisi build
    oedisi debug-component --foreground your_component

Testing component initialization
++++++++++++++++++++++++++++++++

We can test the description of a component and it's initialization without
a full simulation::

    oedisi test-description --component-desc component/component_definition.json --parameters inputs.json


Output::

    ...
    Initialized broker
    Waiting for initialization
    Testing dynamic input names
    ✓
    Testing dynamic output names
    ✓

.. click:: oedisi.tools:cli
   :prog: oedisi
   :nested: full
