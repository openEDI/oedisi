"""Metrics for comparing voltages and power flows from algorithms:

For voltages:
- Mean absolute relative error.
- Mean squared relative error.

For angles:
- Mean absolute angle error."""

import click
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
except ImportError:
    _has_dependencies = False
else:
    _has_dependencies = True


@click.command()
@click.option(
    "--path",
    default=Path("."),
    type=click.Path(),
    help="path to the measurement .feather files",
)
@click.option(
    "--metric",
    default="MSRE",
    type=click.Choice(["MARE", "RMSRE", "MAAE"]),
    help="metric to be used for evaluation",
)
@click.option(
    "--angle-unit",
    default="radians",
    type=click.Choice(["radians", "degrees"]),
    help="Unit of estimated voltages",
)
def evaluate_estimate(path, metric, angle_unit):
    """Evaluate the estimate of the algorithm against the measurements.

    The measurements are assumed to be in the form of .feather files.

    \b
    True voltages:
    - voltage_real.feather
    - voltage_imag.feather

    \b
    Estimated voltages
    - voltage_mag.feather
    - voltage_angle.feather

    \b
    Metrics:
    - MARE: Mean absolute relative error.
    - RMSRE: Root mean squared relative error.
    - MAAE: Mean absolute angle error.

    \f
    Parameters
    ----------

    path : Path
        Path to the folder containing the measurement files.

    metric : str
        Metric to be used for evaluation. The options are:
    """
    path = Path(path)
    if not _has_dependencies:
        raise ImportError("numpy and pandas are required to do this.")
    # measurement files have columns with buses along with a time column
    true_voltages_real = pd.read_feather(path / "voltage_real.feather")
    true_voltages_imag = pd.read_feather(path / "voltage_imag.feather")

    estimated_magnitude = pd.read_feather(path / "voltage_mag.feather")
    estimated_angle = pd.read_feather(path / "voltage_angle.feather")

    time = true_voltages_real["time"]
    estimated_time = estimated_magnitude["time"]
    common_time = set(time).intersection(estimated_time)

    true_voltages_real = true_voltages_real[
        true_voltages_real["time"].isin(common_time)
    ]
    true_voltages_imag = true_voltages_imag[
        true_voltages_imag["time"].isin(common_time)
    ]
    estimated_magnitude = estimated_magnitude[
        estimated_magnitude["time"].isin(common_time)
    ]
    estimated_angle = estimated_angle[estimated_angle["time"].isin(common_time)]

    estimated_magnitude = estimated_magnitude.groupby("time").last().reset_index()
    estimated_angle = estimated_angle.groupby("time").last().reset_index()

    assert list(true_voltages_real["time"]) == list(
        estimated_magnitude["time"]
    ), f"""Time does not match between true voltages and estimated magnitudes:
    
    {list(true_voltages_real["time"])} vs {list(estimated_magnitude["time"])}"""

    # Strip time column from voltages
    true_voltages_real = true_voltages_real.drop(columns=["time"]).reset_index(
        drop=True
    )
    true_voltages_imag = true_voltages_imag.drop(columns=["time"]).reset_index(
        drop=True
    )
    estimated_magnitude = estimated_magnitude.drop(columns=["time"]).reset_index(
        drop=True
    )
    estimated_angle = estimated_angle.drop(columns=["time"]).reset_index(drop=True)
    if angle_unit == "degrees":  # convert to radians
        estimated_angle = estimated_angle * np.pi / 180

    # Convert true voltages to magnitude and angles
    true_magnitudes = np.hypot(true_voltages_real, true_voltages_imag)
    true_angles = np.arctan2(true_voltages_imag, true_voltages_real)

    nonzero_parts = true_magnitudes != 0
    assert (
        true_magnitudes.columns == estimated_magnitude.columns
    ).all(), "Columns do not match between estimated and true voltages."
    true_mag = np.abs(true_magnitudes)
    # Perform evaluation based on the selected metric
    if metric == "MARE":
        # Calculate mean absolute relative error
        magnitude_error = (
            np.mean(
                np.array(np.abs(true_mag - np.abs(estimated_magnitude)) / true_mag)[
                    nonzero_parts
                ]
            )
            * 100
        )
        click.echo(magnitude_error)
    elif metric == "RMSRE":
        # Calculate root mean squared relative error
        magnitude_error = np.sqrt(
            np.mean(
                np.array(np.square(true_mag - np.abs(estimated_magnitude)) / true_mag)[
                    nonzero_parts
                ]
            )
            * 100
        )
        click.echo(magnitude_error)
    elif metric == "MAAE":
        angle_difference = np.abs(true_angles - estimated_angle)
        angle_difference[angle_difference >= np.pi] = (
            2 * np.pi - angle_difference[angle_difference >= np.pi]
        )
        mean_absolute_angle_error = np.mean(
            np.array(angle_difference)[nonzero_parts] * 180 / np.pi
        )
        click.echo(mean_absolute_angle_error)
    else:
        click.echo("Invalid metric selected.")
