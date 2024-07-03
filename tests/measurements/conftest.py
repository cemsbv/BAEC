import datetime
from typing import List

import pytest

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measured_settlement import MeasuredSettlement
from baec.measurements.measured_settlement_series import MeasuredSettlementSeries
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    SettlementRodMeasurementStatus,
    StatusMessage,
    StatusMessageLevel,
)
from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)
from baec.project import Project


@pytest.fixture
def valid_settlement_rod_measurement_input() -> dict:
    return dict(
        project=Project(id_="P-001", name="Project 1"),
        device=MeasurementDevice(id_="BR_003", qr_code="QR-003"),
        object_id="ZB-02",
        date_time=datetime.datetime(2024, 4, 9, 0, 0, 0),
        coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(28992, 5709),
        rod_top_x=123340.266,
        rod_top_y=487597.154,
        rod_top_z=0.807,
        rod_length=2.0,
        rod_bottom_z=-1.193,
        ground_surface_z=0.419,
        status_messages=[
            StatusMessage(code=0, description="OK", level=StatusMessageLevel.OK),
        ],
        temperature=12.0,
        voltage=4232,
    )


@pytest.fixture
def valid_settlement_rod_measurement(
    valid_settlement_rod_measurement_input: dict,
) -> SettlementRodMeasurement:
    return SettlementRodMeasurement(**valid_settlement_rod_measurement_input)


@pytest.fixture
def example_settlement_rod_measurements() -> List[SettlementRodMeasurement]:
    project = Project(id_="P-001", name="Project 1")
    device = MeasurementDevice(id_="BR_003", qr_code="QR-003")
    object_id = "ZB-02"
    date_time_start = datetime.datetime(2024, 4, 9, 0, 0, 0)
    coordinate_reference_systems = CoordinateReferenceSystems.from_epsg(28992, 5709)
    rod_top_x_start = 123340.266
    rod_top_y_start = 487597.154
    rod_top_z_start = 0.807
    rod_length = 2.0
    rod_bottom_z_start = -1.193
    ground_surface_z_start = 0.419
    status_messages = [
        StatusMessage(code=0, description="OK", level=StatusMessageLevel.OK),
    ]
    temperature = 12.0
    voltage = 4232

    measurements = []
    for i in range(10):
        rod_top_x = rod_top_x_start + 0.05 * i
        rod_top_y = rod_top_y_start - 0.03 * i
        rod_top_z = rod_top_z_start - 0.01 * i
        rod_bottom_z = rod_bottom_z_start - 0.1 * i
        ground_surface_z = ground_surface_z_start - 0.1 * i
        date_time = date_time_start + datetime.timedelta(days=i)
        measurements.append(
            SettlementRodMeasurement(
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
        )

    return measurements


@pytest.fixture
def example_settlement_rod_measurement_series(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> SettlementRodMeasurementSeries:
    return SettlementRodMeasurementSeries(
        measurements=example_settlement_rod_measurements
    )


@pytest.fixture
def valid_measured_settlement_input() -> dict:
    return dict(
        project=Project(id_="P-001", name="Project 1"),
        object_id="ZB-02",
        start_date_time=datetime.datetime(2024, 4, 9, 4, 0, 0),
        date_time=datetime.datetime(2024, 4, 17, 4, 0, 0),
        horizontal_units="metre",
        vertical_units="metre",
        fill_thickness=0.5,
        settlement=1.5,
        x_displacement=0.25,
        y_displacement=0.75,
        status=SettlementRodMeasurementStatus.OK,
        status_messages=[
            StatusMessage(code=0, description="OK", level=StatusMessageLevel.OK),
        ],
    )


@pytest.fixture
def example_measured_settlements(
    example_settlement_rod_measurements: List[SettlementRodMeasurement],
) -> List[MeasuredSettlement]:
    measured_settlements = []
    for measurement in example_settlement_rod_measurements:
        measured_settlements.append(
            MeasuredSettlement.from_settlement_rod_measurement(
                measurement=measurement,
                zero_measurement=example_settlement_rod_measurements[0],
            )
        )
    return measured_settlements


@pytest.fixture
def example_measured_settlement_series(
    example_settlement_rod_measurement_series: SettlementRodMeasurementSeries,
) -> MeasuredSettlementSeries:
    return MeasuredSettlementSeries(series=example_settlement_rod_measurement_series)
