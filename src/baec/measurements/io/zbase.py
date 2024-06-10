from __future__ import annotations

import uuid
from os import PathLike

import pandas as pd
from pandas._typing import ReadCsvBuffer

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    SettlementRodMeasurementStatus,
)
from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)
from baec.project import Project

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
    IOError
        If ZBASE file cannot be parsed by Pandas
    """
    # create dummy uuid string
    id_ = str(uuid.uuid4())

    # read zbase csv
    try:
        df = pd.read_csv(
            filepath_or_buffer,
            names=[
                "object_id",
                "date_time",
                "status",
                "rod_top",
                "rod_bottom",
                "ground_surface_z",
                "z",
                "surface_level_z",
                "settlement",
                "x",
                "y",
            ],
            header=None,
        )
    except pd.errors.ParserError as e:
        raise IOError(f"Errors encountered while parsing contents of a file: \n {e}")
    # parse datatime string
    df["date_time"] = pd.to_datetime(df["date_time"], dayfirst=False, yearfirst=False)
    # create SettlementRodMeasurement objects
    measurements = []
    for _, row in df.iterrows():
        measurements.append(
            SettlementRodMeasurement(
                project=Project(id_=id_, name=project_name),
                device=MeasurementDevice(id_=id_),
                object_id=row.get("object_id"),
                date_time=row.get("date_time"),
                coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                    28992, 5709
                ),
                rod_top_x=row.get("x"),
                rod_top_y=row.get("y"),
                rod_top_z=row.get("rod_top"),
                rod_length=abs(row.get("rod_bottom") - row.get("rod_top")),
                rod_bottom_z=row.get("rod_bottom"),
                ground_surface_z=row.get("ground_surface_z"),
                status=SettlementRodMeasurementStatus(
                    _map.get(row.get("status"), "unknown")
                ),
            )
        )

    return SettlementRodMeasurementSeries(measurements)
