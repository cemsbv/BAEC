import datetime
from copy import deepcopy
from typing import Any, Type

import pytest

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measured_settlement import MeasuredSettlement
from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    SettlementRodMeasurementStatus,
    StatusMessage,
    StatusMessageLevel,
)
from baec.project import Project


def test_measured_settlement_init_with_valid_input() -> None:
    """Test initialization of MeasuredSettlement with valid input."""
    project = Project(id_="P-001", name="Project 1")
    object_id = "ZB-02"
    start_date_time = datetime.datetime(2024, 4, 9, 4, 0, 0)
    date_time = datetime.datetime(2024, 4, 17, 16, 15, 0)
    horizontal_units = "metre"
    vertical_units = "metre"
    fill_thickness = 0.5
    settlement = 1.5
    x_displacement = 0.25
    y_displacement = 0.75
    status = SettlementRodMeasurementStatus.OK
    status_messages = [
        StatusMessage(code=0, description="OK", level=StatusMessageLevel.OK),
    ]

    measured_settlement = MeasuredSettlement(
        project=project,
        object_id=object_id,
        start_date_time=start_date_time,
        date_time=date_time,
        horizontal_units=horizontal_units,
        vertical_units=vertical_units,
        fill_thickness=fill_thickness,
        settlement=settlement,
        x_displacement=x_displacement,
        y_displacement=y_displacement,
        status=status,
        status_messages=status_messages,
    )

    assert measured_settlement.project == project
    assert measured_settlement.object_id == object_id
    assert measured_settlement.start_date_time == start_date_time
    assert measured_settlement.date_time == date_time
    assert measured_settlement.horizontal_units == horizontal_units
    assert measured_settlement.vertical_units == vertical_units
    assert measured_settlement.fill_thickness == fill_thickness
    assert measured_settlement.settlement == settlement
    assert measured_settlement.x_displacement == x_displacement
    assert measured_settlement.y_displacement == y_displacement
    assert measured_settlement.status == status
    assert measured_settlement.status_messages == status_messages

    assert measured_settlement.days == pytest.approx(8.51, abs=0.001)


@pytest.mark.parametrize(
    "parameter,invalid_input,expected_error",
    [
        ("project", None, TypeError),
        ("object_id", None, TypeError),
        ("object_id", "", ValueError),
        ("start_date_time", "2024-02-07", TypeError),
        ("date_time", 1, TypeError),
        (
            "date_time",
            datetime.datetime(2024, 2, 9),
            ValueError,
        ),  # date_time < start_date_time
        ("horizontal_units", 1, TypeError),
        ("vertical_units", 1, TypeError),
        ("fill_thickness", "1", TypeError),
        ("fill_thickness", -1.0, ValueError),
        ("settlement", "1", TypeError),
        ("x_displacement", "1", TypeError),
        ("y_displacement", "1", TypeError),
        ("status", 1, TypeError),
    ],
)
def test_measured_settlement_with_invalid_input(
    valid_measured_settlement_input: dict,
    parameter: str,
    invalid_input: Any,
    expected_error: Type[Exception],
) -> None:
    """Test initialization of MeasuredSettlement with invalid input."""
    valid_measured_settlement_input[parameter] = invalid_input
    with pytest.raises(expected_error, match=parameter):
        MeasuredSettlement(**valid_measured_settlement_input)


def test_from_settlement_rod_settlement(
    valid_settlement_rod_measurement: SettlementRodMeasurement,
) -> None:
    """Test constructor method from_measured_settlement_rod_measurement."""
    zero_measurement = deepcopy(valid_settlement_rod_measurement)
    measurement = deepcopy(zero_measurement)
    measurement._date_time = datetime.datetime(2024, 4, 10, 0, 0, 0)
    measurement._rod_top_x += 1.0
    measurement._rod_top_y -= 1.0
    measurement._rod_bottom_z -= 0.25

    # Valid input
    measured_settlement = MeasuredSettlement.from_settlement_rod_measurement(
        measurement=measurement,
        zero_measurement=zero_measurement,
    )

    assert isinstance(measured_settlement, MeasuredSettlement)
    assert measured_settlement.project == measurement.project
    assert measured_settlement.object_id == measurement.object_id
    assert measured_settlement.start_date_time == zero_measurement.date_time
    assert measured_settlement.date_time == measurement.date_time
    assert measured_settlement.days == 1.0
    assert measured_settlement.fill_thickness == 0.419 - (-1.193 - 0.25)
    assert measured_settlement.settlement == 0.25
    assert measured_settlement.x_displacement == 1.0
    assert measured_settlement.y_displacement == -1.0
    assert (
        measured_settlement.horizontal_units
        == measurement.coordinate_reference_systems.horizontal_units
    )
    assert (
        measured_settlement.vertical_units
        == measurement.coordinate_reference_systems.vertical_units
    )
    assert measured_settlement.status == measurement.status
    assert measured_settlement.status_messages == measurement.status_messages

    # Invalid measurement: None
    with pytest.raises(TypeError, match="measurement"):
        MeasuredSettlement.from_settlement_rod_measurement(
            measurement=None,
            zero_measurement=zero_measurement,
        )

    # Invalid zero-measurement: None
    with pytest.raises(TypeError, match="zero_measurement"):
        MeasuredSettlement.from_settlement_rod_measurement(
            measurement=measurement,
            zero_measurement=None,
        )

    # Invalid: both measurements have different projects
    measurement_other = deepcopy(measurement)
    measurement_other._project = Project(id_="P-002", name="Project 2")

    with pytest.raises(ValueError, match="project"):
        MeasuredSettlement.from_settlement_rod_measurement(
            measurement=measurement_other,
            zero_measurement=zero_measurement,
        )

    # Invalid: both measurements have different object ids
    measurement_other = deepcopy(measurement)
    measurement_other._object_id = "ZB-20"

    with pytest.raises(ValueError, match="object"):
        MeasuredSettlement.from_settlement_rod_measurement(
            measurement=measurement_other,
            zero_measurement=zero_measurement,
        )

    # Invalid: both measurements have different coordinate references systems
    measurement_other = deepcopy(measurement)
    measurement_other._coordinate_reference_systems = (
        CoordinateReferenceSystems.from_epsg(28992, 5710)
    )

    with pytest.raises(ValueError, match="coordinate reference systems"):
        MeasuredSettlement.from_settlement_rod_measurement(
            measurement=measurement_other,
            zero_measurement=zero_measurement,
        )


def test_measured_settlement_to_dict() -> None:
    """Test to_dict method are generated without error."""
    project = Project(id_="P-001", name="Project 1")
    object_id = "ZB-02"
    start_date_time = datetime.datetime(2024, 4, 9, 4, 0, 0)
    date_time = datetime.datetime(2024, 4, 17, 4, 0, 0)
    days = (date_time - start_date_time).total_seconds() / 86400.0
    horizontal_units = "metre"
    vertical_units = "metre"
    fill_thickness = 0.5
    settlement = 1.5
    x_displacement = 0.25
    y_displacement = 0.75
    status = SettlementRodMeasurementStatus.OK
    status_messages = [
        StatusMessage(code=0, description="OK", level=StatusMessageLevel.OK),
    ]

    measured_settlement = MeasuredSettlement(
        project=project,
        object_id=object_id,
        start_date_time=start_date_time,
        date_time=date_time,
        horizontal_units=horizontal_units,
        vertical_units=vertical_units,
        fill_thickness=fill_thickness,
        settlement=settlement,
        x_displacement=x_displacement,
        y_displacement=y_displacement,
        status=status,
        status_messages=status_messages,
    )

    assert measured_settlement.to_dict() == {
        "project_id": project.id,
        "project_name": project.name,
        "object_id": object_id,
        "start_date_time": start_date_time,
        "date_time": date_time,
        "days": days,
        "fill_thickness": fill_thickness,
        "settlement": settlement,
        "x_displacement": x_displacement,
        "y_displacement": y_displacement,
        "horizontal_units": horizontal_units,
        "vertical_units": vertical_units,
        "status": status.value,
        "status_messages": "(code=0, description=OK, level=OK)",
    }
