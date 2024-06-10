import datetime
from copy import deepcopy
from typing import List

import pyproj
import pytest

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

    # Different objects
    measurements = deepcopy(example_settlement_rod_measurements)
    measurements[0]._object_id = "ZB-20"

    with pytest.raises(ValueError, match="object"):
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
            df.iloc[i]["coordinate_epsg_code"]
            == measurement.coordinate_reference_system.to_epsg()
        )
        assert df.iloc[i]["date_time"] == measurement.date_time
        assert df.iloc[i]["x"] == measurement.x
        assert df.iloc[i]["y"] == measurement.y
        assert df.iloc[i]["z"] == measurement.z
        assert df.iloc[i]["rod_length"] == measurement.rod_length
        assert df.iloc[i]["plate_bottom_z"] == measurement.plate_bottom_z
        assert (
            df.iloc[i]["plate_bottom_z_uncorrected"]
            == measurement.plate_bottom_z_uncorrected
        )
        assert df.iloc[i]["ground_surface_z"] == measurement.ground_surface_z
        assert df.iloc[i]["status"] == measurement.status.value
        assert df.iloc[i]["temperature"] == measurement.temperature
        assert df.iloc[i]["voltage"] == measurement.voltage
        assert df.iloc[i]["comment"] == measurement.comment
