from oedisi.types.common import BROKER_SERVICE, API_FILE, HeathCheck
from fastapi.testclient import TestClient
from click.testing import CliRunner
from oedisi.tools import cli
from pathlib import Path
import importlib
import pytest
import sys

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
        if folder.is_dir() and folder.name != "kubernetes":
            sys.path.insert(1, str(folder.absolute()))
            assert False, f"{list(build_path.iterdir())}"
            module = importlib.import_module('server') 
            app = getattr(module, "app")  
            client = TestClient(app)
            response = client.get("/")
            assert response.status_code == 200
            HeathCheck.validate(response.json())
            sys.path.remove(str(folder.absolute()))
    