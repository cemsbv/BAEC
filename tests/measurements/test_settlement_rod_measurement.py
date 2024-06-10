import datetime

import pyproj
import pytest

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
    coordinate_reference_system = pyproj.CRS.from_user_input(28992)
    x = 123340.266
    y = 487597.154
    z = 0.807
    rod_length = 2.0
    plate_bottom_z = -1.193
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
        coordinate_reference_system=coordinate_reference_system,
        x=x,
        y=y,
        z=z,
        rod_length=rod_length,
        plate_bottom_z=plate_bottom_z,
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
    assert measurement.coordinate_reference_system == coordinate_reference_system
    assert measurement.x == x
    assert measurement.y == y
    assert measurement.z == z
    assert measurement.rod_length == rod_length
    assert measurement.ground_surface_z == ground_surface_z
    assert measurement.plate_bottom_z == plate_bottom_z
    assert measurement.status == status
    assert measurement.plate_bottom_z_uncorrected == plate_bottom_z_uncorrected
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_coordinate_reference_system() -> (
    None
):
    """Test initialization of settlement rod measurement with invalid coordinate reference system."""
    # Invalid coordinate_reference_system: None
    with pytest.raises(TypeError, match="coordinate_reference_system"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_system=None,
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_x() -> None:
    """Test initialization of settlement rod measurement with invalid x."""
    # Invalid x: String value
    with pytest.raises(TypeError, match="x"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x="123340.266",
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_y() -> None:
    """Test initialization of settlement rod measurement with invalid y."""
    # Invalid y: None
    with pytest.raises(TypeError, match="y"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=None,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_z() -> None:
    """Test initialization of settlement rod measurement with invalid z."""
    # Invalid z: String value
    with pytest.raises(TypeError, match="z"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z="0.807",
            rod_length=2.0,
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length="2.0",
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=-2.0,
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
            ground_surface_z="0.419",
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_plate_bottom_z() -> None:
    """Test initialization of settlement rod measurement with invalid plate_bottom_z."""
    # Invalid plate_bottom_z: String value
    with pytest.raises(TypeError, match="plate_bottom_z"):
        SettlementRodMeasurement(
            project=Project(id_="P-001", name="Project 1"),
            device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
            object_id="ZB-02",
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z="-1.193",
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
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
            coordinate_reference_system=pyproj.CRS.from_user_input(28992),
            x=123340.266,
            y=487597.154,
            z=0.807,
            rod_length=2.0,
            plate_bottom_z=-1.193,
            ground_surface_z=0.419,
            status=SettlementRodMeasurementStatus.OK,
            temperature=12.0,
            voltage=4232,
            comment=123,
        )
