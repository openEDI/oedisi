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

Once the build process is complete, the containers can be launched by either Docker-compose 
(all images will run on the local machine) or using Kubernetes (enables orchestration across multiple 
machines). Navigate to the build folder and execute following command to lauch all images in the 
build folder.  

Running containers using Docker-compose::

    docker compose up

Stopping containers using Docker-compose::

    docker compose down

Alternately, Kubernetes setup files can be used to orchestrate the launch of all the required containers.
Navigate to the ``kubernetes`` folder inside the build folder. It should contain ``deployment.yml`` and 
``service.yml`` files. Use the command below to run the model within the Kubernetes cluster. 
It is to be noted that these files can be modified to serve a unique usecases.

Running containers using Kubernetes::

    kubectl apply -f deployment.yml
    kubectl apply -f service.yml

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
