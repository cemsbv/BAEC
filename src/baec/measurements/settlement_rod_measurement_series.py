from __future__ import annotations

from typing import List

import pandas as pd

from baec.measurements.settlement_rod_measurement import SettlementRodMeasurement


class SettlementRodMeasurementSeries:
    """
    Represents a series of measurements for a single settlement rod.
    """

    def __init__(self, measurements: List[SettlementRodMeasurement]) -> None:
        """
        Initializes a SettlementRodMeasurementSeries object.

        Parameters
        ----------
        measurements : List[SettlementRodMeasurement]
            The list of measurements for the settlement rod.

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If the list of measurements is empty.
            If the measurements are not for the same project, device or object.
        """

        # Initialize all attributes using private setters.
        self._set_measurements(measurements)

    def _set_measurements(self, value: List[SettlementRodMeasurement]) -> None:
        """Private setter for measurements attribute."""

        # Check if the input is a list of SettlementRodMeasurement objects.
        if not all(isinstance(item, SettlementRodMeasurement) for item in value):
            raise TypeError(
                "Expected 'List[SettlementRodMeasurement]' type for 'measurements' attribute."
            )

        # Check if the list is not empty.
        if not value:
            raise ValueError("Empty list not allowed for 'measurements' attribute.")

        # Check that the measurements are for the same project.
        projects = []
        for measurement in value:
            if measurement.project not in projects:
                projects.append(measurement.project)
        if len(projects) > 1:
            raise ValueError("All measurements must be for the same project.")

        # Check that the measurements are for the same device.
        measurement_devices = []
        for measurement in value:
            if measurement.device not in measurement_devices:
                measurement_devices.append(measurement.device)
        if len(measurement_devices) > 1:
            raise ValueError("All measurements must be for the same device.")

        # Check that the measurements are for the same object.
        object_ids = []
        for measurement in value:
            if measurement.object_id not in object_ids:
                object_ids.append(measurement.object_id)
        if len(object_ids) > 1:
            raise ValueError("All measurements must be for the same measured object.")

        # Organize the list of measurements in chronological order.
        self._measurements = sorted(value, key=lambda x: x.date_time)

    @property
    def measurements(self) -> List[SettlementRodMeasurement]:
        """
        The list of measurements for the settlement rod.
        They are organized in chronological order.
        """
        return self._measurements

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the series of measurements to a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with the measurements. The columns of the DataFrame are:
            project_id, project_name, device_id, device_qr_code, object_id,
            coordinate_epsg_code, date_time, x, y, z, rod_length, plate_bottom_z
            plate_bottom_z_uncorrected, ground_surface_z, status, temperature,
            voltage, comment.
        """
        # Initialize an empty DataFrame.
        df = pd.DataFrame()

        # Add columns to the DataFrame.
        df["project_id"] = [measurement.project.id for measurement in self.measurements]
        df["project_name"] = [
            measurement.project.name for measurement in self.measurements
        ]
        df["device_id"] = [measurement.device.id for measurement in self.measurements]
        df["device_qr_code"] = [
            measurement.device.qr_code for measurement in self.measurements
        ]
        df["object_id"] = [measurement.object_id for measurement in self.measurements]
        df["coordinate_epsg_code"] = [
            measurement.coordinate_reference_system.to_epsg()
            for measurement in self.measurements
        ]
        df["date_time"] = pd.to_datetime(
            [measurement.date_time for measurement in self.measurements]
        )
        df["x"] = [measurement.x for measurement in self.measurements]
        df["y"] = [measurement.y for measurement in self.measurements]
        df["z"] = [measurement.z for measurement in self.measurements]
        df["rod_length"] = [measurement.rod_length for measurement in self.measurements]
        df["plate_bottom_z"] = [
            measurement.plate_bottom_z for measurement in self.measurements
        ]
        df["plate_bottom_z_uncorrected"] = [
            measurement.plate_bottom_z_uncorrected for measurement in self.measurements
        ]
        df["ground_surface_z"] = [
            measurement.ground_surface_z for measurement in self.measurements
        ]
        df["status"] = [measurement.status.value for measurement in self.measurements]
        df["temperature"] = [
            measurement.temperature for measurement in self.measurements
        ]
        df["voltage"] = [measurement.voltage for measurement in self.measurements]
        df["comment"] = [measurement.comment for measurement in self.measurements]

        return df
