from copy import deepcopy
from typing import List

import pytest
from matplotlib import pyplot as plt
from pandas import show_versions

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import SettlementRodMeasurement
from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)
from baec.project import Project


def test_settlement_rod_measurement_series_init_with_valid_input(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> None:
    """Test initialization of SettlementRodMeasurementSeries with valid input."""

    # Create series from measurements in chronological order.
    series = SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements
    )

    assert series.measurements == example_settlement_rod_measurements

    # Check that the measurements are in chronological order.
    assert sorted(series.measurements, key=lambda x: x.date_time) == series.measurements

    # Create series from measurements in inverse chronological order.
    series = SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements[::-1]
    )

    assert series.measurements == example_settlement_rod_measurements

    # Check that the measurements are in chronological order.
    assert sorted(series.measurements, key=lambda x: x.date_time) == series.measurements


def test_settlement_rod_measurement_series_init_with_invalid_measurements(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> None:
    """Test initialization of SettlementRodMeasurementSeries with invalid measurements."""

    # Empty list
    with pytest.raises(ValueError, match="measurements"):
        SettlementRodMeasurementSeries(measurements=[])

    # Incorrect type: One item is a string.
    measurements = deepcopy(example_settlement_rod_measurements)
    measurements[0] = "invalid"
    with pytest.raises(TypeError):
        SettlementRodMeasurementSeries(measurements=measurements)

    # Different projects
    measurements = deepcopy(example_settlement_rod_measurements)
    measurements[0]._project = Project(id_="P-002", name="Project 2")

    with pytest.raises(ValueError, match="project"):
        SettlementRodMeasurementSeries(measurements=measurements)

    # Different devices
    measurements = deepcopy(example_settlement_rod_measurements)
    measurements[0]._device = MeasurementDevice(id_="BR_004", qr_code="QR-004")

    with pytest.raises(ValueError, match="device"):
        SettlementRodMeasurementSeries(measurements=measurements)

    # Different measured objects
    measurements = deepcopy(example_settlement_rod_measurements)
    measurements[0]._object_id = "ZB-20"

    with pytest.raises(ValueError, match="object"):
        SettlementRodMeasurementSeries(measurements=measurements)

    # Different coordinate reference systems (horizontal)
    measurements = deepcopy(example_settlement_rod_measurements)
    measurements[
        0
    ]._coordinate_reference_systems = CoordinateReferenceSystems.from_epsg(28992, 5710)

    with pytest.raises(ValueError, match="coordinate reference systems"):
        SettlementRodMeasurementSeries(measurements=measurements)

    # Different coordinate reference systems (vertical)
    measurements = deepcopy(example_settlement_rod_measurements)
    measurements[
        0
    ]._coordinate_reference_systems = CoordinateReferenceSystems.from_epsg(31370, 5709)

    with pytest.raises(ValueError, match="coordinate reference systems"):
        SettlementRodMeasurementSeries(measurements=measurements)


def test_settlement_rod_measurement_series_to_dataframe_method(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> None:
    """Test the to_dataframe method of SettlementRodMeasurementSeries."""
    series = SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements
    )

    df = series.to_dataframe()

    # Check that the DataFrame has the correct number of rows.
    assert len(df) == len(example_settlement_rod_measurements)

    # Check that the DataFrame has the correct data.
    for i, measurement in enumerate(example_settlement_rod_measurements):
        assert df.iloc[i]["project_id"] == measurement.project.id
        assert df.iloc[i]["device_id"] == measurement.device.id
        assert df.iloc[i]["object_id"] == measurement.object_id
        assert (
            df.iloc[i]["coordinate_horizontal_epsg_code"]
            == measurement.coordinate_reference_systems.horizontal.to_epsg()
        )
        assert (
            df.iloc[i]["coordinate_vertical_epsg_code"]
            == measurement.coordinate_reference_systems.vertical.to_epsg()
        )
        assert df.iloc[i]["coordinate_horizontal_units"] == (
            measurement.coordinate_reference_systems.horizontal_units
        )
        assert df.iloc[i]["coordinate_vertical_units"] == (
            measurement.coordinate_reference_systems.vertical_units
        )
        assert df.iloc[i]["coordinate_vertical_datum"] == (
            measurement.coordinate_reference_systems.vertical_datum
        )
        assert df.iloc[i]["date_time"] == measurement.date_time
        assert df.iloc[i]["rod_top_x"] == measurement.rod_top_x
        assert df.iloc[i]["rod_top_y"] == measurement.rod_top_y
        assert df.iloc[i]["rod_top_z"] == measurement.rod_top_z
        assert df.iloc[i]["rod_length"] == measurement.rod_length
        assert df.iloc[i]["rod_bottom_z"] == measurement.rod_bottom_z
        assert (
            df.iloc[i]["rod_bottom_z_uncorrected"]
            == measurement.rod_bottom_z_uncorrected
        )
        assert df.iloc[i]["ground_surface_z"] == measurement.ground_surface_z
        assert df.iloc[i]["status"] == measurement.status.value
        assert df.iloc[i]["temperature"] == measurement.temperature
        assert df.iloc[i]["voltage"] == measurement.voltage
        assert df.iloc[i]["comment"] == measurement.comment


def test_plot_x_time(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> None:
    """Test plot_x_time method are generated without error."""

    show = False

    series = SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements
    )

    # Plot without giving axes
    ax = series.plot_x_time()
    if show:
        plt.show()

    # Plot giving axes
    _, ax = plt.subplots()
    series.plot_x_time(ax)
    if show:
        plt.show()

    plt.close("all")


def test_plot_y_time(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> None:
    """Test plot_y_time method are generated without error."""

    show = False

    series = SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements
    )

    # Plot without giving axes
    ax = series.plot_y_time()
    if show:
        plt.show()

    # Plot giving axes
    _, ax = plt.subplots()
    series.plot_y_time(ax)
    if show:
        plt.show()

    plt.close("all")


def test_plot_z_time(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> None:
    """Test plot_z_time method are generated without error."""

    show = False

    series = SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements
    )

    # Plot without giving axes
    ax = series.plot_z_time()
    if show:
        plt.show()

    # Plot giving axes
    _, ax = plt.subplots()
    series.plot_z_time(ax)
    if show:
        plt.show()

    plt.close("all")


def test_plot_xyz_time(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> None:
    """Test plot_xyz_time method are generated without error."""

    show = False

    series = SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements
    )

    # Plot without giving axes
    series.plot_xyz_time()
    if show:
        plt.show()

    plt.close()


def test_plot_xy_plan_view(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> None:
    """Test plot_xy_plan_view method are generated without error."""

    show = False

    series = SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements
    )

    # Plot without giving axes
    ax = series.plot_xy_plan_view()
    if show:
        plt.show()

    # Plot giving axes
    _, ax = plt.subplots()
    series.plot_xy_plan_view(ax)
    if show:
        plt.show()

    plt.close("all")
