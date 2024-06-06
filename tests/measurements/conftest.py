import datetime
from typing import List

import pyproj
import pytest

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
    coordinate_reference_system = pyproj.CRS.from_user_input(28992)
    x = 123340.266
    y = 487597.154
    z_start = 0.807
    rod_length = 2.0
    plate_bottom_z = -1.193
    ground_surface_z = 0.419
    status = SettlementRodMeasurementStatus.OK
    temperature = 12.0
    voltage = 4232
    comment = "No comment"

    measurements = []
    for i in range(10):
        z = z_start - 0.01 * i
        date_time = date_time_start + datetime.timedelta(days=i)
        measurements.append(
            SettlementRodMeasurement(
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
        )

    return measurements
