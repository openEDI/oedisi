from oedisi.tools import cli
import pytest
import json
from pathlib import Path
from click.testing import CliRunner


@pytest.fixture
def base_path() -> Path:
    """Get the current folder of the test."""
    return Path(__file__).parent


def test_build_run(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["build"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["run"])
    assert result.exit_code == 0


def test_debug(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["debug-component", "--foreground", "comp_xyz"])
    assert result.exit_code == 0


def test_build_description(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["build"])
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "test-description",
            "--component-desc",
            "component2/component_definition.json",
        ],
    )
    assert result.exit_code == 0


def test_bad_build_description(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["build"])
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "test-description",
            "--component-desc",
            "component3/component_definition.json",
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "test-description",
            "--component-desc",
            "component3/bad_component_definition.json",
        ],
    )
    assert result.exit_code == 1


def test_build_with_helics_cli_options(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "build",
            "--helics-port", "23456",
            "--helics-core-type", "zmq",
            "--helics-broker-key", "mykey",
        ],
    )
    assert result.exit_code == 0

    with open("build/system_runner.json") as f:
        runner_config = json.load(f)
    broker_cmd = runner_config["federates"][-1]["exec"]
    assert "--port 23456" in broker_cmd
    assert "-t zmq" in broker_cmd
    assert "--brokerkey mykey" in broker_cmd


def test_helics_options_rejected_for_multicontainer(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["build", "-m", "--helics-port", "23456"])
    assert result.exit_code != 0
    assert "not supported for multi-container" in result.output
