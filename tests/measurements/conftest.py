import datetime
from typing import List

import pytest

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    SettlementRodMeasurementStatus,
)
from baec.project import Project


@pytest.fixture
def example_settlement_rod_measurements() -> List[SettlementRodMeasurement]:
    project = Project(id_="P-001", name="Project 1")
    device = MeasurementDevice(id_="BR_003", qr_code="QR-003")
    object_id = "ZB-02"
    date_time_start = datetime.datetime(2024, 4, 9, 4, 0, 0)
    coordinate_reference_systems = CoordinateReferenceSystems.from_epsg(28992, 5709)
    rod_top_x_start = 123340.266
    rod_top_y_start = 487597.154
    rod_top_z_start = 0.807
    rod_length = 2.0
    plate_bottom_z = -1.193
    ground_surface_z = 0.419
    status = SettlementRodMeasurementStatus.OK
    temperature = 12.0
    voltage = 4232
    comment = "No comment"

    measurements = []
    for i in range(10):
        rod_top_x = rod_top_x_start + 0.05 * i
        rod_top_y = rod_top_y_start - 0.03 * i
        rod_top_z = rod_top_z_start - 0.01 * i
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
                rod_bottom_z=plate_bottom_z,
                ground_surface_z=ground_surface_z,
                status=status,
                temperature=temperature,
                voltage=voltage,
                comment=comment,
            )
        )

    return measurements
