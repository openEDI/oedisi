import click
import json
import os
import subprocess
import time

from gadal.componentframework.basic_component import (
    basic_component,
    ComponentDescription
)
from gadal.componentframework.mock_component import MockComponent
from gadal.componentframework.system_configuration import (
    RunnerConfig,
    generate_runner_config,
    WiringDiagram,
    Component,
)
from .pausing_broker import PausingBroker
from .testing_broker import TestingBroker

@click.group()
def cli():
    pass


def bad_type_checker(type, x):
    "Does not check types"
    return True


def get_basic_component(filename):
    # before, the runner would use the directory given _in_ the component description
    # which may be inaccurate
    comp_desc = ComponentDescription.parse_file(filename)
    comp_desc.directory = os.path.dirname(filename)  
    return basic_component(comp_desc, bad_type_checker)


@cli.command()
@click.option("--target-directory", default="build", type=click.Path(),
              help="Target directory to put the system in")
@click.option("--system", default="system.json", type=click.Path(),
              help="Wiring diagram json to build")
@click.option("--component-dict", default="components.json", type=click.Path(),
              help="JSON Dictionary of component folders")
def build(target_directory, system, component_dict):
    """Build to the simulation folder

    Parameters
    ----------
    target_directory : str (default="build")
        build path
    system : str (default="system.json")
        path to wiring diagram json
    component_dict : str (default="components.json")
        path to JSON dictionary of component folders
    """
    click.echo(f"Loading the components defined in {component_dict}")
    with open(component_dict, 'r') as f:
        component_dict_of_files = json.load(f)
        component_types = {
            name: get_basic_component(component_file)
            for name, component_file in component_dict_of_files.items()
        }

    click.echo(f"Loading system json {system}")
    wiring_diagram = WiringDiagram.parse_file(system)

    click.echo(f"Building system in {target_directory}")
    runner_config = generate_runner_config(
        wiring_diagram, component_types, target_directory=target_directory
    )
    with open(f"{target_directory}/system_runner.json", "w") as f:
        f.write(runner_config.json(indent=2))


@cli.command()
@click.option("--runner", default="build/system_runner.json", type=click.Path())
def run(runner):
    "Calls out to helics run command"
    subprocess.run(["helics", "run", f"--path={runner}"])


@cli.command()
@click.option("--runner", default="build/system_runner.json", type=click.Path())
def run_with_pause(runner):
    """Helics broker is in the foreground, and we allow user input
    to block time. Currently waiting on pyhelics version 3.3.1"""
    new_system, new_path, _ = remove_from_json(runner, "broker")
    background_runner = subprocess.Popen(["helics", "run", f"--path={new_path}"])
    broker = PausingBroker(len(new_system.federates))
    broker.run()
    background_runner.wait()


@cli.command()
@click.option("--target-directory", default="build", type=click.Path())
@click.option("--component-desc", type=click.Path())
@click.option("--parameters", default=None)
def test_description(target_directory, component_desc, parameters):
    """Test component intialization from component description

    Parameters
    ----------

    target_directory : str
        build location

    component_desc : str
        filepath to component_description.json to test

    parameters : str
        filepath to parameters json (default is parameters={})

    Process
    -------

    Get inputs and outputs from component_desc
    Create a wiring diagram for component
        and a "do-nothing" component with parameters for the corresponding
        inputs and outputs (basically recorder federate?)
    Create and run system with wiring diagram
    """

    comp_desc = ComponentDescription.parse_file(component_desc)
    comp_desc.directory = os.path.dirname(component_desc)

    if parameters is None:
        parameters = {}
    else:
        with open(parameters) as f:
            parameters = json.load(f)

    inputs = list(map(lambda x: x.port_name, comp_desc.dynamic_inputs))
    outputs = list(map(lambda x: x.port_name, comp_desc.dynamic_outputs))
    w = WiringDiagram.empty()
    component = Component(name="component", type="UserComponent",
                          parameters=parameters)
    tester = Component(name="tester", type="MockComponent", parameters={
        "inputs": outputs,
        "outputs": {x.port_name: x.type for x in comp_desc.dynamic_inputs}
    })
    w.add_component(component)
    w.add_component(tester)
    for i in outputs:
        w.add_link(component.port(i).connect(tester.port(i)))

    for i in inputs:
        w.add_link(tester.port(i).connect(component.port(i)))

    component_types = {
        "MockComponent": MockComponent,
        "UserComponent": basic_component(
            comp_desc,
            bad_type_checker
        )
    }
    runner_config = generate_runner_config(w, component_types, target_directory=target_directory)
    runner_config, _ = remove_from_runner_config(runner_config, "broker")
    with open(f"{target_directory}/system_runner.json", "w") as f:
        f.write(runner_config.json())

    background_runner = subprocess.Popen(
        ["helics", "run", f"--path={target_directory}/system_runner.json"]
    )
    broker = TestingBroker(len(runner_config.federates))
    federate_inputs, federate_outputs = broker.run()
    background_runner.kill()
    print("Testing dynamic input names")
    assert sorted(list(map(
        lambda x: x.port_name, comp_desc.dynamic_inputs
    ))) == sorted(list(map(
        lambda x: x.split("/")[1], federate_inputs["component"]
    )))
    print("✓")
    print("Testing dynamic output names")
    assert sorted(list(map(
        lambda x: "component/" + x.port_name, comp_desc.dynamic_outputs
    ))) == sorted(federate_outputs["component"])
    print("✓")



def remove_from_runner_config(runner_config, element):
    "Remove federate from configuration"
    within_feds = [fed for fed in runner_config.federates
                        if fed.name != element]
    without_feds = [fed for fed in runner_config.federates
                        if fed.name == element]
    new_config = RunnerConfig(
        name = runner_config.name,
        federates = within_feds
    )
    return new_config, without_feds


def remove_from_json(system_json, element):
    "Remove federate from configuration and resave with revised.json"
    with open(system_json, "r") as f:
        runner_config = RunnerConfig.parse_obj(json.load(f))
        new_config, without_feds = remove_from_runner_config(
            runner_config,
            element
        )

        new_path = system_json + "revised.json"
        click.echo(f"Saving new json to {new_path}")
        with open(new_path, "w") as f:
            f.write(new_config.json())
        return new_config, new_path, without_feds


@cli.command()
@click.option("--runner", default="build/system_runner.json", type=click.Path())
@click.option("--foreground", type=str)
def debug_component(runner, foreground):
    """
    Run system runner json with one component in the JSON

    Parameters
    ----------

    runner : str
        filepath to system runner json

    foreground : str
        name of component

    We remove one component from system_runner.json
    and then call helics run in the background with our new json.
    and then run our debugging component in standard in / standard out.
    """
    _, new_path, foreground_federates = remove_from_json(runner, foreground)
    assert len(foreground_federates) == 1
    foreground_fed = foreground_federates[0]
    directory = os.path.join(os.path.dirname(new_path), foreground_fed.directory)
    click.echo("Removing")
    click.echo(f"""
Name      : {foreground_fed.name}
Directory : {directory}
Command   : {foreground_fed.exec}
    """)

    click.echo("Starting system (note you may have to kill manually)")
    helics_sim = subprocess.Popen(["helics", "run", f"--path={new_path}"])
    click.echo(f"Running component {foreground_fed.name} in foreground")
    _ = subprocess.run(foreground_fed.exec.split(), cwd=directory)
    helics_sim.wait()


if __name__ == "__main__":
    cli()
