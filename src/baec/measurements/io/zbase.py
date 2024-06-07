from __future__ import annotations

import uuid
from os import PathLike

import pandas as pd
import pyproj
from pandas._typing import ReadCsvBuffer

from baec.measurements.settlement_rod_measurement import (
    MeasurementDevice,
    Project,
    SettlementRodMeasurement,
    SettlementRodMeasurementStatus,
)
from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)

_map = {
    0: "ok",
    1: "ok",
    2: "disturbed",
    3: "expired",
    4: "relocated",
    5: "rod_is_extended",
    6: "crooked",
    7: "deselected",
    8: "deselected",
    9: "fictional",
    10: "unknown",
}


def measurements_from_zbase(
    filepath_or_buffer: str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str],
    project_name: str,
) -> SettlementRodMeasurementSeries:
    """
    Parse a zBase csv into SettlementRodMeasurementSeries object.

    Parameters
    ----------
    filepath_or_buffer : str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str],
        Any valid string path is acceptable.
    project_name : str
        The name of the project.

    Returns
    -------
    series : SettlementRodMeasurementSeries
        A SettlementRodMeasurementSeries object.

    Raises
    ------
    TypeError
        If the input types are incorrect.
    ValueError
        If the list of measurements is empty.
        If the measurements are not for the same project, device or object.
    """
    # create dummy uuid string
    id_ = str(uuid.uuid4())

    # read zbase csv
    df = pd.read_csv(
        filepath_or_buffer,
        names=[
            "object_id",
            "date_time",
            "status",
            "rod_top",
            "rod_bottom",
            "surface_level_z",
            "z",
            "ground_surface_z",
            "settlement",
            "x",
            "y",
        ],
        header=None,
    )
    # parse datatime string
    df["date_time"] = pd.to_datetime(df["date_time"], dayfirst=False, yearfirst=False)
    offset = df["surface_level_z"][0]
    # create SettlementRodMeasurement objects
    measurements = []
    for _, row in df.iterrows():
        measurements.append(
            SettlementRodMeasurement(
                project=Project(id_=id_, name=project_name),
                device=MeasurementDevice(id_=id_),
                object_id=row["object_id"],
                date_time=row["date_time"],
                coordinate_reference_system=pyproj.CRS.from_user_input(28992),
                x=row["x"],
                y=row["y"],
                z=offset
                - row["z"],  # Transform depth to depth with respect to reference level
                rod_length=abs(row["rod_bottom"] - row["rod_top"]),
                plate_bottom_z=row["rod_bottom"],
                ground_surface_z=row["surface_level_z"],
                status=SettlementRodMeasurementStatus(
                    _map.get(row["status"], "unknown")
                ),
            )
        )

    return SettlementRodMeasurementSeries(measurements)
