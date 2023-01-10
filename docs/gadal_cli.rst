`gadal` CLI
===========

In `gadal.gadal_tools`, there is a `cli` tool called `gadal`.
There are tools to build, run, and debug simulations as well
as test component description JSONs.

Occasionally, the HELICS runner will fail to start and may need
to be killed.


A `component-dict` will be a JSON file with names to component definitions::

    {
      "ComponentOne": "component1/component_definition.json",
      "ComponentTwo": "component2/component_definition.json"
    }


.. click:: gadal.gadal_tools:cli
   :prog: gadal
   :nested: full
