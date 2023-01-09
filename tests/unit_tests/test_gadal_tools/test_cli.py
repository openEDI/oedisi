import os
import json
from gadal.gadal_tools import cli
import pytest
import importlib
from pathlib import Path
from click.testing import CliRunner

@pytest.fixture
def base_path() -> Path:
    """Get the current folder of the test"""
    return Path(__file__).parent

def test_build_run(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)

    runner = CliRunner()
    result = runner.invoke(cli, ['build'])
    assert result.exit_code == 0
    result = runner.invoke(cli, ['run'])
    assert result.exit_code == 0

def test_debug(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)

    runner = CliRunner()
    result = runner.invoke(
        cli, ['debug-component', '--foreground', 'comp_xyz']
    )
    assert result.exit_code == 0

def test_build_description(
        base_path: Path,
        monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(base_path)

    runner = CliRunner()
    result = runner.invoke(cli, ['build'])
    assert result.exit_code == 0
    result = runner.invoke(
        cli, [
            'test-description',
            '--component-desc',
            'component2/component_definition.json'
        ]
    )
    assert result.exit_code == 0
