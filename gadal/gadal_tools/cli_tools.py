import click
import json
import os
import subprocess

from gadal.componentframework.basic_component import (
    basic_component,
    ComponentDescription
)
from gadal.componentframework.system_configuration import (
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
    background_runner = subprocess.Popen(["helics", "run", f"--path"])
    from pausing_broker import PausingBroker
    broker = PausingBroker()
    broker.run()



@cli.command()
def test_component():
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


@cli.command()
def debug_component():
    click.echo("Put one component in debug mode")
    return NotImplemented

if __name__ == "__main__":
    cli()
