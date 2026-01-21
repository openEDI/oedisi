from oedisi.tools import cli
import pytest
from pathlib import Path
from click.testing import CliRunner
import numpy as np


@pytest.fixture
def base_path() -> Path:
    """Get the current folder of the test."""
    return Path(__file__).parent


def test_metrics(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path)

    runner = CliRunner()
    result = runner.invoke(
        cli, ["evaluate-estimate", "--path", Path("test_data"), "--metric", "MARE"]
    )
    assert result.exit_code == 0
    assert np.isclose(float(result.output), 0.6281941853348966)

    result = runner.invoke(
        cli, ["evaluate-estimate", "--path", Path("test_data"), "--metric", "RMSRE"]
    )
    assert result.exit_code == 0
    assert np.isclose(float(result.output), 5.4879027532795135)

    result = runner.invoke(
        cli, ["evaluate-estimate", "--path", Path("test_data"), "--metric", "MAAE"]
    )
    assert result.exit_code == 0
    assert np.isclose(float(result.output), 1.7543213971636016)
