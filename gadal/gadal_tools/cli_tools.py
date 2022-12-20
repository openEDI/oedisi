import click
import json
import os
import subprocess
import time

from gadal.componentframework.basic_component import (
    basic_component,
    ComponentDescription
)
from gadal.componentframework.system_configuration import (
    RunnerConfig,
    generate_runner_config,
    WiringDiagram,
)

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
@click.option("--target-directory", default="build", type=str,
              help="Target directory to put the system in")
@click.option("--system", default="system.json", type=str,
              help="Wiring diagram json to build")
@click.option("--component-dict", default="components.json", type=str,
              help="JSON Dictionary of component folders")
def build(target_directory, system, component_dict):
    "Build to the simulation folder"
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
@click.option("--runner", default="build/system_runner.json")
def run(runner):
    subprocess.run(["helics", "run", f"--path={runner}"])


@cli.command()
@click.option("--runner", default="build/system_runner.json")
def run_with_pause(runner):
    # Helics broker is in the foreground, and we allow user input
    # to block time. Currently waiting on pyhelics version 3.3.1
    #
    with open(runner, "r") as f:
        system_json = RunnerConfig.parse_obj(json.load(f))
        new_system, brokers = remove_from_json(system_json, "broker")
        assert len(brokers) == 1

    new_path = runner + "revised.json"
    click.echo(f"Saving new json without broker to {new_path}")
    with open(new_path, "w") as f:
        f.write(new_system.json())

    background_runner = subprocess.Popen(["helics", "run", f"--path={new_path}"])
    from pausing_broker import PausingBroker
    broker = PausingBroker(len(new_system.federates))
    time.sleep(3)
    broker.run()
    background_runner.wait()



@cli.command()
def test_component():  # Data fuzzing
    click.echo("Test the component in a complement system")
    # First we create a wiring diagram with our component
    # connected to a tester
    #
    # The tester will send a test data of each input,
    # then it'll listen for the output.
    #
    # We want to start a HELICS simulation, then confirm
    # that things got connected (maybe run for a bit), then we want to shut the simulation
    # down fast. Maybe we can start our federate early and then cancel?
    return NotImplemented


def remove_from_json(system_json, component):
    within_feds = [fed for fed in system_json.federates
                        if fed.name != component]
    without_feds = [fed for fed in system_json.federates
                        if fed.name == component]
    new_system = RunnerConfig(
        name = system_json.name,
        federates = within_feds
    )
    return new_system, without_feds


@cli.command()
@click.option("--runner", default="build/system_runner.json")
@click.option("--without")
def debug_component(runner, without):  # one of them should be stdin/stdout
    # Idea 1: We remove one component from system_runner.json
    # and then call helics run in the background with our new json.
    # and then run our debugging component in standard in / standard out.
    # Note that this requires the helics broker to have the true number of federates.
    with open(runner, "r") as f:
        system_json = RunnerConfig.parse_obj(json.load(f))
        new_system, without_feds = remove_from_json(system_json, without)
        assert len(without_feds) == 1
        without_fed = without_feds[0]
    new_path = runner + "revised.json"
    click.echo(f"Saving new json to {new_path}")
    with open(new_path, "w") as f:
        f.write(new_system.json())

    directory = os.path.join(os.path.dirname(new_path), without_fed.directory)
    click.echo("Removing")
    click.echo(f"""
Name      : {without_fed.name}
Directory : {directory}
Command   : {without_fed.exec}
    """)

    click.echo("Starting system (note you may have to kill manually)")
    helics_sim = subprocess.Popen(["helics", "run", f"--path={new_path}"])
    click.echo("Running component {without_fed.name} in foreground")
    _ = subprocess.run(without_fed.exec.split(), cwd=directory)
    helics_sim.wait()
    #component_proc.wait()


if __name__ == "__main__":
    cli()
