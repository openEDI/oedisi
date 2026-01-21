import importlib
import json
import time
import subprocess
import os
import logging

from pathlib import Path

import pytest
from click.testing import CliRunner
from fastapi.testclient import TestClient

from oedisi.tools import cli
from oedisi.types.common import BROKER_SERVICE, HeathCheck

from oedisi.componentframework.system_configuration import (
    WiringDiagram,
)
from requests.exceptions import ConnectionError

API_FILE = "server.py"
TEST_SIMULATION = "test_sim"
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@pytest.fixture
def base_path() -> Path:
    """Get the current folder of the test"""
    return Path(__file__).parent


@pytest.fixture
def test_mc_build(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)
    runner = CliRunner()

    broker_path = base_path / BROKER_SERVICE
    assert (
        broker_path.exists()
    ), "Broker federate should be implemented before building a multicontainer problem."

    api_implementation = broker_path / API_FILE
    assert api_implementation.exists(), (
        f"A valid REST API implementatiion should exist in {api_implementation} "
        "before building a multicontainer problem."
    )

    requirements_file = broker_path / "requirements.txt"
    assert requirements_file.exists(), (
        "All components should have a valid requirements.txt file listing required "
        "python packages for the build."
    )

    result = runner.invoke(cli, ["build", "-m", "-i", TEST_SIMULATION])
    assert result.exit_code == 0


@pytest.mark.usefixtures("test_mc_build")
def test_api_heath_endpoint(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    build_path = base_path / "build" / TEST_SIMULATION

    assert build_path.exists(), "Build path for the test project does not exist."
    assert (
        build_path / "docker-compose.yml"
    ).exists(), "Build path for the test project does not exist."

    for folder in base_path.iterdir():
        if folder.is_dir():
            print(folder.name)
            if folder.name in ["component1", "component2", "broker"]:
                assert (
                    folder / "server.py"
                ).exists(), f"Server.py does not exist for path {folder}"
                monkeypatch.syspath_prepend(folder.absolute())
                module = importlib.import_module("server")
                app = getattr(module, "app")
                client = TestClient(app)
                response = client.get("/")
                assert response.status_code == 200
                HeathCheck.model_validate(response.json())
            else:
                assert not (folder / "server.py").exists()


@pytest.mark.usefixtures("test_mc_build")
def test_api_run(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    build_path = base_path / "build" / TEST_SIMULATION

    assert build_path.exists(), "Build path for the test project does not exist."
    assert (
        build_path / "docker-compose.yml"
    ).exists(), "Build path for the test project does not exist."

    payload = json.load(open(base_path / "system.json"))
    wiring_diagram = WiringDiagram(**payload)

    clients = {}
    for folder in base_path.iterdir():
        if folder.is_dir():
            if folder.name in ["component1", "component2", "broker"]:
                assert (
                    folder / "server.py"
                ).exists(), f"Server.py does not exist for path {folder}"
                monkeypatch.syspath_prepend(folder.absolute())
                print("folder: ", folder)
                print("Current dir:", os.getcwd())

                module_name = f"{folder.name}_server"
                spec = importlib.util.spec_from_file_location(
                    module_name, folder / "server.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                app = getattr(module, "app")
                client = TestClient(app)
                clients[folder.name] = client

    assert BROKER_SERVICE in clients, (
        "No broker client in list of tested services. "
        f"Available services {list(clients.keys())}"
    )
    client = clients[BROKER_SERVICE]
    # Connection error is raised as the broker running, but not all components are up yet.
    # wheb broker make s post request to components, they are not available yet.
    with pytest.raises(ConnectionError):
        client.post(
            "/configure/",
            json=wiring_diagram.model_dump(),
        )


@pytest.mark.usefixtures("test_mc_build")
def test_docker_compose(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    build_path = base_path / "build" / TEST_SIMULATION
    assert build_path.exists(), "Build path for the test project does not exist."
    monkeypatch.chdir(build_path)

    with subprocess.Popen(
        ["docker", "compose", "up", "-d", "--build", "--force-recreate"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        assert (
            proc.returncode != 0
        ), f"docker-compose failed with {proc.returncode}: {proc.stderr.read()}"
        stdout = b""
        start = time.time()
        fail = True
        stderr = b""
        while (time.time() - start) < 120:
            bytes = proc.stdout.read()
            err_msg = proc.stderr.read()
            stdout += bytes
            stderr += err_msg
            output = stdout.decode("utf8") + stderr.decode("utf8")
            assert (
                "failed to read dockerfile" not in output.lower()
                and "no service selected" not in output.lower()
                and "invalid compose project" not in output.lower()
                and "error response from daemon:" not in output.lower()
            ), f"Failed in docker compose up.\n{stdout}\n{stderr}"

            count = output.count("Started") + output.count("Running")
            if count >= 3:
                fail = False
                break
            time.sleep(0.1)

    logging.debug(f"{stdout}")
    logging.debug(f"{stderr}")
    subprocess.Popen(
        ["docker", "compose", "down"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert not fail, f"Timeout Exceeded on docker-compose:\n{stdout}\n{stderr}"
