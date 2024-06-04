import datetime

import pyproj
import pytest

from baec.measurements.settlement_rod_measurements import SettlementRodMeasurement


def test_settlement_rod_measurement_init_with_valid_input() -> None:
    """Test initialization of settlement rod measurement with valid input."""
    date_time = datetime.datetime(2024, 4, 9, 4, 0, 0)
    rod_id = "BR_003"
    point_id = "ZB-02"
    coordinate_epsg_code = 28992
    x = 123340.266
    y = 487597.154
    z = 0.807
    vertical_offset = 2.0
    ground_surface_z = 0.419
    plate_bottom_z = -1.193
    plate_bottom_z_uncorrected = -1.193
    temperature = 12.0
    voltage = 4232
    comment = "No comment"
    coordinate_reference_system = pyproj.CRS.from_user_input(coordinate_epsg_code)

    measurement = SettlementRodMeasurement(
        date_time=date_time,
        rod_id=rod_id,
        point_id=point_id,
        coordinate_epsg_code=coordinate_epsg_code,
        x=x,
        y=y,
        z=z,
        vertical_offset=vertical_offset,
        ground_surface_z=ground_surface_z,
        plate_bottom_z=plate_bottom_z,
        temperature=temperature,
        voltage=voltage,
        comment=comment,
    )

    assert measurement.date_time == date_time
    assert measurement.rod_id == rod_id
    assert measurement.point_id == point_id
    assert measurement.coordinate_epsg_code == coordinate_epsg_code
    assert measurement.x == x
    assert measurement.y == y
    assert measurement.z == z
    assert measurement.vertical_offset == vertical_offset
    assert measurement.ground_surface_z == ground_surface_z
    assert measurement.plate_bottom_z == plate_bottom_z
    assert measurement.plate_bottom_z_uncorrected == plate_bottom_z_uncorrected
    assert measurement.temperature == temperature
    assert measurement.voltage == voltage
    assert measurement.comment == comment
    assert measurement.coordinate_reference_system == coordinate_reference_system


def test_settlement_rod_measurement_init_with_invalid_date_time() -> None:
    """Test initialization of settlement rod measurement with invalid date_time."""
    # Invalid date_time: None
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=None,
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_rod_id() -> None:
    """Test initialization of settlement rod measurement with invalid rod_id."""
    # Invalid rod_id: None
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id=None,
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )

    # Invalid rod_id: Empty string
    with pytest.raises(ValueError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_point_id() -> None:
    """Test initialization of settlement rod measurement with invalid point_id."""
    # Invalid point_id: None
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id=None,
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )

    # Invalid rod_id: Empty string
    with pytest.raises(ValueError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_coordinate_epsg_code() -> None:
    """Test initialization of settlement rod measurement with invalid coordinate_epsg_code."""
    # Invalid coordinate_epsg_code: None
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=None,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )

    # Invalid coordinate_epsg_code: Negative value
    with pytest.raises(ValueError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=-28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_point_x() -> None:
    """Test initialization of settlement rod measurement with invalid point_x."""
    # Invalid point_x: String value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x="123340.266",
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_point_y() -> None:
    """Test initialization of settlement rod measurement with invalid point_y."""
    # Invalid point_y: None
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=None,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_point_z() -> None:
    """Test initialization of settlement rod measurement with invalid point_z."""
    # Invalid point_z: String value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z="0.807",
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_rod_length() -> None:
    """Test initialization of settlement rod measurement with invalid rod_length."""
    # Invalid point_z: String value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset="2.0",
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )

    # Invalid rod_length: Negative value
    with pytest.raises(ValueError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=-2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_ground_surface_z() -> None:
    """Test initialization of settlement rod measurement with invalid ground_surface_z."""
    # Invalid ground_surface_z: String value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z="-0.419",
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_ground_plate_z() -> None:
    """Test initialization of settlement rod measurement with invalid ground_plate_z."""
    # Invalid ground_plate_z: String value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z="1.193",
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_temperature() -> None:
    """Test initialization of settlement rod measurement with invalid temperature."""
    # Invalid temperature: String value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature="12.0",
            voltage=4232,
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_voltage() -> None:
    """Test initialization of settlement rod measurement with invalid voltage."""
    # Invalid voltage: String value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage="4232",
            comment="No comment",
        )


def test_settlement_rod_measurement_init_with_invalid_comment() -> None:
    """Test initialization of settlement rod measurement with invalid comment."""
    # Invalid comment: Integer value
    with pytest.raises(TypeError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992,
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment=123,
        )


def test_settlement_rod_measurement_init_with_invalid_coordinate_reference_system() -> (
    None
):
    """Test initialization of settlement rod measurement with invalid coordinate reference system."""
    with pytest.raises(pyproj.exceptions.CRSError):
        SettlementRodMeasurement(
            date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
            rod_id="BR_003",
            point_id="ZB-02",
            coordinate_epsg_code=28992111,  # no coordinate system corresponds to this epsg code.
            x=123340.266,
            y=487597.154,
            z=0.807,
            vertical_offset=2.0,
            ground_surface_z=0.419,
            plate_bottom_z=-1.193,
            temperature=12.0,
            voltage=4232,
            comment="No comment",
        )
