import subprocess
import shutil
import click
import yaml
import json
import os
from pathlib import Path


from distutils.dir_util import copy_tree

from oedisi.componentframework.basic_component import (
    basic_component,
    ComponentDescription,
)
from oedisi.componentframework.mock_component import MockComponent
from oedisi.componentframework.system_configuration import (
    RunnerConfig,
    generate_runner_config,
    WiringDiagram,
    Component,
)
from .pausing_broker import PausingBroker
from .testing_broker import TestingBroker
from .metrics import evaluate_estimate

from oedisi.types.common import (
    APP_NAME,
    BASE_DOCKER_IMAGE,
    BROKER_SERVICE,
    DOCKER_HUB_USER,
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
@click.option(
    "--target-directory",
    default="build",
    type=click.Path(),
    help="Target directory to put the system in",
)
@click.option(
    "--system",
    default="system.json",
    type=click.Path(),
    help="Wiring diagram json to build",
)
@click.option(
    "--component-dict",
    default="components.json",
    type=click.Path(),
    help="path to JSON Dictionary of component folders",
)
@click.option(
    "-m",
    "--multi-container",
    is_flag=True,
    default=False,
    show_default=True,
    help="Use the flag to create docker-compose config files for a multi-container implementation.",
)
@click.option(
    "-p", "--broker-port", default=8766, show_default=True, help="Pass the broker port."
)
def build(
    target_directory,
    system,
    component_dict,
    multi_container,
    broker_port,
    node_port=30000,
):
    """Build to the simulation folder

    Examples::

        oedisi build

        oedisi build --component-dict components.json --system scenario.json

    \f
    Parameters
    ----------

    target_directory : str (default="build")
        build path
    system : str (default="system.json")
        path to wiring diagram json
    component_dict : str (default="components.json")
        path to JSON dictionary of component folders
    multi_container: bool
        A boolean specifying whether or not we're using the multi-container approach
    broker_port: float
        The port of the broker. If using kubernetes, is internal to k8s
    node_port: float (default=30000)
        The port exposed externally from k8s for external access on localhost
    """
    click.echo(f"Loading the components defined in {component_dict}")
    with open(component_dict, "r") as f:
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

    yaml_file_path = f"{target_directory}/docker-compose.yml"

    if multi_container:
        validate_optional_inputs(wiring_diagram, component_dict_of_files)
        edit_docker_files(wiring_diagram, target_directory)
        create_docker_compose_file(wiring_diagram, target_directory, broker_port)
        clone_broker(yaml_file_path, target_directory)
        create_kubernetes_deployment(
            wiring_diagram, target_directory, broker_port, node_port
        )


def validate_optional_inputs(
    wiring_diagram: WiringDiagram, component_dict_of_files: dict
):
    for component in wiring_diagram.components:
        assert hasattr(
            component, "host"
        ), f"host parameter required for component {component.name} for multi-continer model build"
        assert hasattr(
            component, "container_port"
        ), f"post parameter required for component {component.name} for multi-continer model build"


def create_kubernetes_deployment(
    wiring_diagram: WiringDiagram, target_directory, broker_port, node_port
):
    kube_folder = os.path.join(target_directory, "kubernetes")
    if not os.path.exists(kube_folder):
        os.mkdir(kube_folder)

    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": f"{APP_NAME}-service",
        },
        "spec": {
            "type": "NodePort",
            "selector": {"app": APP_NAME},
            "ports": [{"port": broker_port, "nodePort": node_port}],
        },
    }

    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": f"{APP_NAME}-deployment", "labels": {"app": APP_NAME}},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": APP_NAME}},
            "template": {
                "metadata": {"labels": {"app": APP_NAME}},
                "spec": {"containers": []},
            },
        },
    }

    container = {}
    for component in wiring_diagram.components:
        container["name"] = component.name.replace("_", "-")
        container["image"] = component.image
        container["ports"] = [{"containerPort": component.container_port}]
        deployment["spec"]["template"]["spec"]["containers"].append(container.copy())

    container["name"] = BROKER_SERVICE.replace("_", "-")
    container["image"] = f"{DOCKER_HUB_USER}/{APP_NAME}_{BROKER_SERVICE}:latest"
    container["ports"] = [{"containerPort": broker_port}]
    deployment["spec"]["template"]["spec"]["containers"].append(container.copy())

    with open(os.path.join(kube_folder, "deployment.yml"), "w") as f:
        yaml.dump(deployment, f)
    with open(os.path.join(kube_folder, "service.yml"), "w") as f:
        yaml.dump(service, f)


def clone_broker(yaml_file_path, target_directory):
    broker_folder = os.path.join(target_directory, "broker")
    if not os.path.exists(broker_folder):
        os.makedirs(broker_folder)
    copy_tree("./broker", broker_folder)
    shutil.copy(yaml_file_path, broker_folder)
    return


def edit_docker_file(file_path, component: Component):
    dir_path = os.path.abspath(os.path.join(file_path, os.pardir))
    server_file = os.path.join(dir_path, "server.py")
    assert os.path.exists(
        server_file
    ), f"Server.py file missing for {component.name}.REST API implementation expected in a server.py file"

    with open(file_path, "w") as f:
        f.write(f"FROM {BASE_DOCKER_IMAGE}\n")
        f.write(f"RUN apt-get update\n")
        f.write(f"RUN apt-get install -y git ssh\n")
        f.write(f"RUN mkdir {component.name}\n")
        f.write(f"COPY  . ./{component.name}\n")
        f.write(f"WORKDIR ./{component.name}\n")
        f.write(f"RUN pip install -r requirements.txt\n")
        f.write(f"EXPOSE {component.container_port}/tcp\n")
        cmd = f'CMD {["python", "server.py", component.host, str(component.container_port)]}\n'
        cmd = cmd.replace("'", '"')
        f.write(cmd)
    pass


def edit_docker_files(wiring_diagram: WiringDiagram, target_directory: str):
    for component in wiring_diagram.components:
        docker_path = os.path.join(target_directory, component.name, "Dockerfile")
        edit_docker_file(docker_path, component)


def create_docker_compose_file(
    wiring_diagram: WiringDiagram, target_directory: str, broker_port: int
):
    config = {"services": {}, "networks": {}}

    config["services"][f"{APP_NAME}_{BROKER_SERVICE}"] = {
        "build": {"context": f"./broker/."},
        "image": f"{DOCKER_HUB_USER}/{APP_NAME}_{BROKER_SERVICE}",
        "ports": [f"{broker_port}:{broker_port}"],
        "networks": {"custom-network": {"ipv4_address": "10.5.0.2"}},
    }

    for component in wiring_diagram.components:
        config["services"][f"{APP_NAME}_{component.name}"] = {
            "build": {"context": f"./{component.name}/."},
            "image": f"{component.image}",
            "ports": [f"{component.container_port}:{component.container_port}"],
            "networks": {"custom-network": {"ipv4_address": component.host}},
        }

    config["networks"] = {
        "custom-network": {
            "driver": "bridge",
            "ipam": {
                "config": [
                    {
                        "subnet": "10.5.0.0/16",
                        "gateway": "10.5.0.1",
                    },
                ]
            },
        }
    }
    yaml_file_path = f"{target_directory}/docker-compose.yml"
    with open(yaml_file_path, "w") as file:
        yaml.dump(config, file)
    return yaml_file_path


@cli.command()
@click.option(
    "--runner",
    default="build/system_runner.json",
    type=click.Path(),
    help="Location of helics run json. Usually build/system_runner.json",
)
def run(runner):
    """Calls out to helics run command

    Examples::

        oedisi run
    """
    subprocess.run(["helics", "run", f"--path={runner}"])


@cli.command()
@click.option(
    "--runner",
    default="build/system_runner.json",
    type=click.Path(),
    help="Location of helics run json. Usually build/system_runner.json",
)
def run_with_pause(runner):
    """Helics broker is run in the foreground, and we allow user input
    to block time.

    Examples::

        oedisi run-with-pause


        Enter next time: [0.0]: 1.0
        Setting time barrier to 1.0

            Name         : comp_abc
            Granted Time : 0.0
            Send Time    : 0.0


            Name         : comp_xyz
            Granted Time : 0.0
            Send Time    : 0.0

    """
    new_system, new_path, _ = remove_from_json(runner, "broker")
    background_runner = subprocess.Popen(["helics", "run", f"--path={new_path}"])
    broker = PausingBroker(len(new_system.federates))
    broker.run()
    background_runner.wait()


@cli.command()
@click.option(
    "--runner",
    default="build/docker-compose.yml",  # build/kubernetes/deployment.yml
    type=click.Path(),
    help="path to the docker-compose or kubernetes deployment file",
)
@click.option(
    "-k",
    "--kubernetes",
    is_flag=True,
    default=False,
    show_default=True,
    help="Use the flag to launch in a kubernetes pod. ",
)
@click.option(
    "-d",
    "--docker-compose",
    is_flag=True,
    default=False,
    show_default=True,
    help="Use the flag to launch in a kubernetes pod. ",
)
def run_mc(runner, kubernetes, docker_compose):
    assert os.path.exists(runner), f"The provied path {runner} does not exist."
    file_name = Path(runner).name.lower()
    os.system("docker system prune --all")
    os.system("docker network prune --all")
    if docker_compose:
        assert (
            file_name == "docker-compose.yml"
        ), f"{file_name} is not a valid docker-compose.yml file"
        build_path = os.path.dirname(os.path.abspath(runner))
        os.chdir(build_path)
        os.system("docker-compose up")
    elif kubernetes:
        assert (
            file_name == "deployment.yml"
        ), f"{file_name} is not a valid deployment.yml file for kubernetes."
        build_path = os.path.dirname(os.path.abspath(runner))
        os.system(f"kubectl apply -f {build_path}")
    else:
        raise Exception("Either -k or -d flag needs to be True.")


@cli.command()
@click.option(
    "--target-directory",
    default="build",
    type=click.Path(),
    help="Target directory to put the system in",
)
@click.option(
    "--component-desc", type=click.Path(), help="Path to component description"
)
@click.option(
    "--parameters",
    default=None,
    help="Path to parameters JSON (default is parameters={})",
)
def test_description(target_directory, component_desc, parameters):
    """Test component intialization from component description

    Examples::

        oedisi test-description --component-desc component/component_definition.json --parameters inputs.json

        Initialized broker
        Waiting for initialization
        Testing dynamic input names
        ✓
        Testing dynamic output names
        ✓


    \f
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
    component = Component(name="component", type="UserComponent", parameters=parameters)
    tester = Component(
        name="tester",
        type="MockComponent",
        parameters={
            "inputs": outputs,
            "outputs": {x.port_name: x.type for x in comp_desc.dynamic_inputs},
        },
    )
    w.add_component(component)
    w.add_component(tester)
    for i in outputs:
        w.add_link(component.port(i).connect(tester.port(i)))

    for i in inputs:
        w.add_link(tester.port(i).connect(component.port(i)))

    component_types = {
        "MockComponent": MockComponent,
        "UserComponent": basic_component(comp_desc, bad_type_checker),
    }
    runner_config = generate_runner_config(
        w, component_types, target_directory=target_directory
    )
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
    assert sorted(list(map(lambda x: x.port_name, comp_desc.dynamic_inputs))) == sorted(
        list(map(lambda x: x.split("/")[1], federate_inputs["component"]))
    )
    print("✓")
    print("Testing dynamic output names")
    assert sorted(
        list(map(lambda x: "component/" + x.port_name, comp_desc.dynamic_outputs))
    ) == sorted(federate_outputs["component"])
    print("✓")


def remove_from_runner_config(runner_config, element):
    "Remove federate from configuration"
    within_feds = [fed for fed in runner_config.federates if fed.name != element]
    without_feds = [fed for fed in runner_config.federates if fed.name == element]
    new_config = RunnerConfig(name=runner_config.name, federates=within_feds)
    return new_config, without_feds


def remove_from_json(system_json, element):
    "Remove federate from configuration and resave with revised.json"
    with open(system_json, "r") as f:
        runner_config = RunnerConfig.parse_obj(json.load(f))
        new_config, without_feds = remove_from_runner_config(runner_config, element)

        new_path = system_json + "revised.json"
        click.echo(f"Saving new json to {new_path}")
        with open(new_path, "w") as f:
            f.write(new_config.json())
        return new_config, new_path, without_feds


@cli.command()
@click.option(
    "--runner",
    default="build/system_runner.json",
    type=click.Path(),
    help="Location of helics run json. Usually build/system_runner.json",
)
@click.option("--foreground", type=str, help="Name of component to run in background")
def debug_component(runner, foreground):
    """
    Run system runner json with one component in the JSON

    We remove one component from system_runner.json
    and then call helics run in the background with our new json.
    and then run our debugging component in standard in / standard out.

    \f
    Parameters
    ----------

    runner : str
        filepath to system runner json

    foreground : str
        name of component
    """
    _, new_path, foreground_federates = remove_from_json(runner, foreground)
    assert len(foreground_federates) == 1
    foreground_fed = foreground_federates[0]
    directory = os.path.join(os.path.dirname(new_path), foreground_fed.directory)
    click.echo("Removing")
    click.echo(
        f"""
Name      : {foreground_fed.name}
Directory : {directory}
Command   : {foreground_fed.exec}
    """
    )

    click.echo("Starting system (note you may have to kill manually)")
    helics_sim = subprocess.Popen(["helics", "run", f"--path={new_path}"])
    click.echo(f"Running component {foreground_fed.name} in foreground")
    _ = subprocess.run(foreground_fed.exec.split(), cwd=directory)
    helics_sim.wait()


cli.add_command(evaluate_estimate)

if __name__ == "__main__":
    cli()
