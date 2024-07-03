import datetime
from typing import Any, Type

import pyproj
import pytest

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    SettlementRodMeasurementStatus,
    StatusMessage,
    StatusMessageLevel,
)
from baec.project import Project


def test_status_message_level_comparison() -> None:
    """Test comparison of status message levels."""
    # OK
    assert StatusMessageLevel.OK == StatusMessageLevel.OK
    assert StatusMessageLevel.OK < StatusMessageLevel.INFO
    assert StatusMessageLevel.OK < StatusMessageLevel.WARNING
    assert StatusMessageLevel.OK < StatusMessageLevel.ERROR

    # INFO
    assert StatusMessageLevel.INFO > StatusMessageLevel.OK
    assert StatusMessageLevel.INFO == StatusMessageLevel.INFO
    assert StatusMessageLevel.INFO < StatusMessageLevel.WARNING
    assert StatusMessageLevel.INFO < StatusMessageLevel.ERROR

    # WARNING
    assert StatusMessageLevel.WARNING > StatusMessageLevel.OK
    assert StatusMessageLevel.WARNING > StatusMessageLevel.INFO
    assert StatusMessageLevel.WARNING == StatusMessageLevel.WARNING
    assert StatusMessageLevel.WARNING < StatusMessageLevel.ERROR

    # ERROR
    assert StatusMessageLevel.ERROR > StatusMessageLevel.OK
    assert StatusMessageLevel.ERROR > StatusMessageLevel.INFO
    assert StatusMessageLevel.ERROR > StatusMessageLevel.WARNING
    assert StatusMessageLevel.ERROR == StatusMessageLevel.ERROR

    # Different types
    assert StatusMessageLevel.OK != 0


def test_status_message_init_with_valid_input() -> None:
    """Test initialization of status message with valid input."""
    code = 0
    description = "OK"
    level = StatusMessageLevel.OK

    status_message = StatusMessage(code=code, description=description, level=level)

    assert status_message.code == code
    assert status_message.description == description
    assert status_message.level == level


def test_status_message_init_with_invalid_input() -> None:
    """Test initialization of status message with invalid input."""
    with pytest.raises(TypeError):
        StatusMessage(code="0", description="OK", level=StatusMessageLevel.OK)

    with pytest.raises(TypeError):
        StatusMessage(code=0, description=0, level=StatusMessageLevel.OK)

    with pytest.raises(ValueError):
        StatusMessage(code=0, description="", level=StatusMessageLevel.OK)

    with pytest.raises(TypeError):
        StatusMessage(code=0, description="OK", level=0)


def test_status_message_to_string() -> None:
    """Test string representation of status message."""
    code = 0
    description = "No comment"
    level = StatusMessageLevel.OK

    status_message = StatusMessage(code=code, description=description, level=level)

    assert status_message.to_string() == "(code=0, description=No comment, level=OK)"


def test_settlement_rod_measurement_init_with_valid_input() -> None:
    """Test initialization of settlement rod measurement with valid input."""
    project = Project(id_="P-001", name="Project 1")
    device = MeasurementDevice(id_="BR_003", qr_code="QR-003")
    object_id = "ZB-02"
    date_time = datetime.datetime(2024, 4, 9, 4, 0, 0)
    coordinate_reference_systems = CoordinateReferenceSystems.from_epsg(28992, 5709)
    rod_top_x = 123340.266
    rod_top_y = 487597.154
    rod_top_z = 0.807
    rod_length = 2.0
    rod_bottom_z = -1.193
    ground_surface_z = 0.419
    status_messages = [
        StatusMessage(code=0, description="OK", level=StatusMessageLevel.OK),
    ]
    temperature = 12.0
    voltage = 4232
    plate_bottom_z_uncorrected = -1.193

    measurement = SettlementRodMeasurement(
        project=project,
        device=device,
        object_id=object_id,
        date_time=date_time,
        coordinate_reference_systems=coordinate_reference_systems,
        rod_top_x=rod_top_x,
        rod_top_y=rod_top_y,
        rod_top_z=rod_top_z,
        rod_length=rod_length,
        rod_bottom_z=rod_bottom_z,
        ground_surface_z=ground_surface_z,
        status_messages=status_messages,
        temperature=temperature,
        voltage=voltage,
    )

    assert measurement.project == project
    assert measurement.device == device
    assert measurement.object_id == object_id
    assert measurement.date_time == date_time
    assert measurement.coordinate_reference_systems == coordinate_reference_systems
    assert measurement.rod_top_x == rod_top_x
    assert measurement.rod_top_y == rod_top_y
    assert measurement.rod_top_z == rod_top_z
    assert measurement.rod_length == rod_length
    assert measurement.ground_surface_z == ground_surface_z
    assert measurement.rod_bottom_z == rod_bottom_z
    assert measurement.status_messages == status_messages
    assert measurement.status == SettlementRodMeasurementStatus.OK
    assert measurement.rod_bottom_z_uncorrected == plate_bottom_z_uncorrected
    assert measurement.temperature == temperature
    assert measurement.voltage == voltage


@pytest.mark.parametrize(
    "parameter,invalid_input,expected_error",
    [
        ("project", None, TypeError),
        ("device", None, TypeError),
        ("object_id", None, TypeError),
        ("object_id", "", ValueError),
        ("date_time", None, TypeError),
        ("coordinate_reference_systems", None, TypeError),
        ("rod_top_x", "123340.266", TypeError),
        ("rod_top_y", None, TypeError),
        ("rod_top_z", "0.807", TypeError),
        ("rod_length", "2.0", TypeError),
        ("rod_length", -2.0, ValueError),
        ("ground_surface_z", "0.419", TypeError),
        ("rod_bottom_z", "-1.193", TypeError),
        ("temperature", "12.0", TypeError),
        ("voltage", "4232", TypeError),
        ("status_messages", None, TypeError),
        ("status_messages", ["OK"], TypeError),
    ],
)
def test_settlement_rod_measurement_init_with_invalid_input(
    valid_settlement_rod_measurement_input: dict,
    parameter: str,
    invalid_input: Any,
    expected_error: Type[Exception],
) -> None:
    """Test initialization of SettlementRodMeasurement with invalid input."""
    valid_settlement_rod_measurement_input[parameter] = invalid_input
    with pytest.raises(expected_error, match=parameter):
        SettlementRodMeasurement(**valid_settlement_rod_measurement_input)


def test_settlement_rod_measurement_status(
    valid_settlement_rod_measurement_input: dict,
) -> None:
    """Test status property of SettlementRodMeasurement."""

    # No status messages
    valid_settlement_rod_measurement_input["status_messages"] = []
    measurement = SettlementRodMeasurement(**valid_settlement_rod_measurement_input)
    assert measurement.status == SettlementRodMeasurementStatus.OK

    # Different status messages with OK as highest level.
    valid_settlement_rod_measurement_input["status_messages"] = [
        StatusMessage(code=5, description="OK", level=StatusMessageLevel.OK),
        StatusMessage(code=1, description="No comments", level=StatusMessageLevel.OK),
    ]
    measurement = SettlementRodMeasurement(**valid_settlement_rod_measurement_input)
    assert measurement.status == SettlementRodMeasurementStatus.OK

    # Different status messages with INFO as highest level.
    valid_settlement_rod_measurement_input["status_messages"] = [
        StatusMessage(code=5, description="OK", level=StatusMessageLevel.OK),
        StatusMessage(code=1, description="INFO", level=StatusMessageLevel.INFO),
    ]
    measurement = SettlementRodMeasurement(**valid_settlement_rod_measurement_input)
    assert measurement.status == SettlementRodMeasurementStatus.INFO

    # Different status messages with WARNING as highest level.
    valid_settlement_rod_measurement_input["status_messages"] = [
        StatusMessage(code=5, description="WARNING", level=StatusMessageLevel.WARNING),
        StatusMessage(code=2, description="INFO", level=StatusMessageLevel.INFO),
    ]
    measurement = SettlementRodMeasurement(**valid_settlement_rod_measurement_input)
    assert measurement.status == SettlementRodMeasurementStatus.WARNING

    # Different status messages with ERROR as highest level.
    valid_settlement_rod_measurement_input["status_messages"] = [
        StatusMessage(code=5, description="WARNING", level=StatusMessageLevel.WARNING),
        StatusMessage(code=10, description="ERROR", level=StatusMessageLevel.ERROR),
    ]
    measurement = SettlementRodMeasurement(**valid_settlement_rod_measurement_input)
    assert measurement.status == SettlementRodMeasurementStatus.ERROR
