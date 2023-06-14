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
