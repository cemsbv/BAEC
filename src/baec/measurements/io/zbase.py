from __future__ import annotations

import datetime
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

_STATUS_MAP = {
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
    FileNotFoundError:
        If filepath_or_buffer is requested but doesn’t exist.
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
                "rod_top_z",
                "rod_bottom_z",
                "ground_surface_z",
                # rod_bottom_z[0] - rod_bottom_z[i]
                "ground_surface_displacement",
                # ground_surface_z[0] - ground_surface_z[i] - ground_surface_displacement[i]
                "fill_thickness",
                # ?
                "rod_top_displacement",
                "rod_top_x",
                "rod_top_y",
            ],
            header=None,
        )
    except pd.errors.ParserError as e:
        raise IOError(f"Errors encountered while parsing contents of a file: \n {e}")
    except FileNotFoundError as e:
        raise FileNotFoundError(e)
    # parse datatime string
    df["date_time"] = pd.to_datetime(df["date_time"], dayfirst=False, yearfirst=False)
    # create SettlementRodMeasurement objects
    measurements = []
    for _, row in df.iterrows():
        measurements.append(
            SettlementRodMeasurement(
                project=Project(id_=id_, name=project_name),
                device=MeasurementDevice(id_=id_),
                object_id=row.get("object_id", ""),
                date_time=row.get("date_time", datetime.datetime.now()),
                coordinate_reference_systems=CoordinateReferenceSystems.from_epsg(
                    28992, 5709
                ),
                rod_top_x=row.get("rod_top_x", 0),
                rod_top_y=row.get("rod_top_y", 0),
                rod_top_z=row.get("rod_top_z", 0),
                rod_length=row.get("rod_top_z", 0) - row.get("rod_bottom_z", 0),
                rod_bottom_z=row.get("rod_bottom_z", 0),
                ground_surface_z=row.get("ground_surface_z", 0),
                status=SettlementRodMeasurementStatus(
                    _STATUS_MAP.get(row.get("status", 10), "unknown")
                ),
            )
        )

    return SettlementRodMeasurementSeries(measurements)
