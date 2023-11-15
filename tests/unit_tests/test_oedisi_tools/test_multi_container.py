from oedisi.types.common import BROKER_SERVICE, API_FILE, HeathCheck
from fastapi.testclient import TestClient
from click.testing import CliRunner
from oedisi.tools import cli
from pathlib import Path
import requests
import subprocess
import importlib
import pytest
import yaml
import time
import sys
import os

@pytest.fixture
def base_path() -> Path:
    """Get the current folder of the test"""
    return Path(__file__).parent

@pytest.fixture
def test_mc_build(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)
    runner = CliRunner()
    
    broker_path = base_path / BROKER_SERVICE
    assert broker_path.exists(), "Broker federate should be implemented before building a multicontainer problem."

    api_implementation = broker_path / API_FILE
    assert api_implementation.exists(), f"A valid REST API implementatiion should exist in {api_implementation} before building a multicontainer problem."    
  
    requirements_file = broker_path / "requirements.txt"
    assert requirements_file.exists(), f"All components should have a valid requirements.txt file listing required python packages for the build."    
              
    result = runner.invoke(cli, ['build', "-m"])
    assert result.exit_code == 0
    
@pytest.mark.usefixtures('test_mc_build')
def test_api_heath_endpoint(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)
    build_path = base_path / "build"
    assert build_path.exists(), "Build path for the test project does not exist."
    for folder in build_path.iterdir():
        if folder.is_dir() and folder.name not in ["kubernetes", 'tester']:
            assert (folder/"server.py").exists(), f"Server.py does not exist for path {folder}"
            sys.path.insert(1, str(folder.absolute()))
            module = importlib.import_module('server') 
            app = getattr(module, "app")  
            client = TestClient(app)
            response = client.get("/")
            assert response.status_code == 200
            HeathCheck.validate(response.json())
            sys.path.remove(str(folder.absolute()))

@pytest.mark.usefixtures('test_mc_build')
def test_api_run(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)
    build_path = base_path / "build"
    assert build_path.exists(), "Build path for the test project does not exist."
    docker_compose_file = build_path / "docker-compose.yml"
    assert docker_compose_file.exists(), "Docker-compose file not found in the build path."
    data = yaml.load(open(docker_compose_file, 'r'), Loader = yaml.Loader)
    services = data["services"]
    mapped_ports = {}
    processes = []
    for service, svc_details  in services.items():
        service = service.replace("oedisi_", "")
        network = svc_details['networks']
        ip = network['custom-network']['ipv4_address']
        port = svc_details['ports'][0].split(":")[0]
        folder = build_path / service
        assert folder.exists(), f"Service folder {folder} does not exist"
        server_file = folder/ "server.py"
        assert server_file.exists(), f"rerver.py does not exist for path {folder}"
        proc = subprocess.Popen(["python", str(server_file), port, port], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        proc
        processes.append(proc)
        mapped_ports[service] = port
    
    time.sleep(2)   
    headers = {
        'Content-Type': 'application/json',
    }
    url = f"http://localhost:{mapped_ports['broker']}/run"
    reply = requests.get(url)
    assert reply.status_code == 200, f"Simulation failure for post request {url}. \nReturned status code: {reply.status_code}.\nError message: {reply.text}"
    
    for p in processes:
        p.terminate()


    