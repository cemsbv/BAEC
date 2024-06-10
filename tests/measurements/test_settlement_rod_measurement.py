import datetime

import pyproj
import pytest

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    SettlementRodMeasurementStatus,
)
from baec.project import Project


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
    status = SettlementRodMeasurementStatus.OK
    temperature = 12.0
    voltage = 4232
    comment = "No comment"
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
        status=status,
        temperature=temperature,
        voltage=voltage,
        comment=comment,
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
    assert measurement.status == status
    assert measurement.rod_bottom_z_uncorrected == plate_bottom_z_uncorrected
    assert measurement.temperature == temperature
    assert measurement.voltage == voltage
    assert measurement.comment == comment


def test_settlement_rod_measurement_init_with_invalid_project() -> None:
    """Test initialization of settlement rod measurement with invalid project."""
    # Invalid project: None
    with pytest.raises(TypeError, match="project"):
        SettlementRodMeasurement(
            project=None,
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_device() -> None:
    """Test initialization of settlement rod measurement with invalid device."""
    # Invalid device: None
    with pytest.raises(TypeError, match="device"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=None,
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_object_id() -> None:
    """Test initialization of settlement rod measurement with invalid object_id."""
    # Invalid point_id: None
    with pytest.raises(TypeError, match="object_id"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id=None,
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )

    # Invalid rod_id: Empty string
    with pytest.raises(ValueError, match="object_id"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_date_time() -> None:
    """Test initialization of settlement rod measurement with invalid date_time."""
    # Invalid date_time: None
    with pytest.raises(TypeError, match="date_time"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=None,
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_coordinate_reference_systems() -> (
    None
):
    """Test initialization of settlement rod measurement with invalid coordinate reference systems."""
    # Invalid coordinate_reference_system: None
    with pytest.raises(TypeError, match="coordinate_reference_systems"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=None,
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_rod_top_x() -> None:
    """Test initialization of settlement rod measurement with invalid rod_top_x."""
    # Invalid rod_top_x: String value
    with pytest.raises(TypeError, match="rod_top_x"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x="123340.266",
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_rod_top_y() -> None:
    """Test initialization of settlement rod measurement with invalid rod_top_y."""
    # Invalid rod_top_y: None
    with pytest.raises(TypeError, match="rod_top_y"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=None,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_rod_top_z() -> None:
    """Test initialization of settlement rod measurement with invalid rod_top_z."""
    # Invalid rod_top_z: String value
    with pytest.raises(TypeError, match="rod_top_z"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z="0.807",
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_rod_length() -> None:
    """Test initialization of settlement rod measurement with invalid rod_length."""
    # Invalid point_z: String value
    with pytest.raises(TypeError, match="rod_length"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length="2.0",
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )

    # Invalid rod_length: Negative value
    with pytest.raises(ValueError, match="rod_length"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=-2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_ground_surface_z() -> None:
    """Test initialization of settlement rod measurement with invalid ground_surface_z."""
    # Invalid ground_surface_z: String value
    with pytest.raises(TypeError, match="ground_surface_z"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z="0.419",
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_rod_bottom_z() -> None:
    """Test initialization of settlement rod measurement with invalid rod_bottom_z."""
    # Invalid rod_bottom_z: String value
    with pytest.raises(TypeError, match="rod_bottom_z"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z="-1.193",
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_temperature() -> None:
    """Test initialization of settlement rod measurement with invalid temperature."""
    # Invalid temperature: String value
    with pytest.raises(TypeError, match="temperature"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature="12.0",
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_voltage() -> None:
    """Test initialization of settlement rod measurement with invalid voltage."""
    # Invalid voltage: String value
    with pytest.raises(TypeError, match="voltage"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage="4232",
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_comment() -> None:
    """Test initialization of settlement rod measurement with invalid comment."""
    # Invalid comment: Integer value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                28992, 5709
            ),
            rod_top_x=123340.266,
            rod_top_y=487597.154,
            rod_top_z=0.807,
            rod_length=2.0,
            rod_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment=123,
        )
