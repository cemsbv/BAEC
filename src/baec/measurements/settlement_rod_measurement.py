from __future__ import annotations

import datetime
from enum import Enum

import pyproj

from baec.measurements.measurement_device import MeasurementDevice
from baec.project import Project


class SettlementRodMeasurementStatus(Enum):
    """Represents the status of a settlement rod measurement."""

    OK = "ok"
    DISTURBED = "disturbed"
    EXPIRED = "expired"
    RELOCATED = "relocated"
    ROD_IS_EXTENDED = "rod_is_extended"
    CROOKED = "crooked"
    DESELECTED = "deselected"
    FICTIONAL = "fictional"
    UNKNOWN = "unknown"


class SettlementRodMeasurement:
    """
    Represents a single settlement rod measurement.
    """

    def __init__(
        self,
        project: Project,
        device: MeasurementDevice,
        object_id: str,
        date_time: datetime.datetime,
        coordinate_reference_system: pyproj.CRS,
        x: float,
        y: float,
        z: float,
        rod_length: float,
        plate_bottom_z: float,
        ground_surface_z: float,
        status: SettlementRodMeasurementStatus,
        temperature: float | None = None,
        voltage: float | None = None,
        comment: str = "",
    ) -> None:
        """
        Initializes a SettlementRodMeasurement object.

        Parameters
        ----------
        project : Project
            The project which the measurement belongs to.
        device : MeasurementDevice
            The measurement device.
        date_time : datetime.datetime
            The date and time of the measurement.
        object_id : str
            The ID of the measured object.
        date_time : datetime.datetime
            The date and time of the measurement.
        coordinate_reference_system : pyproj.CRS
            The coordinate reference system of the spatial measurements.
            It is a `pyproj.CRS` object (see https://pyproj4.github.io/pyproj/stable/api/crs/crs.html).
        x : float
            The X-coordinate of the measurement point. Units are according to the `coordinate_reference_system`.
        y : float
            The Y-coordinate of the measurement point. Units are according to the `coordinate_reference_system`.
        z : float
            The Z-coordinate of the measurement point.
            It is the top of the settlement rod.
            Units are according to the `coordinate_reference_system`.
        rod_length : float
            The length of the settlement rod including the thickness of the settlement plate.
            It is in principle the vertical distance between the measurement point and the bottom of the settlement plate.
            Units are according to the `coordinate_reference_system`.
        plate_bottom_z : float
            The corrected Z-coordinate at the bottom of the settlement plate.
            Note that the bottom of the plate is in principle the original ground surface.
            Units are according to the `coordinate_reference_system`.
        ground_surface_z : float
            The Z-coordinate of the ground surface.
            It is in principle the top of the fill, if present.
            Units are according to the `coordinate_reference_system`.
        status: SettlementRodMeasurementStatus
            The status of the measurement.
        temperature : float or None, optional
            The temperature at the time of measurement in [°C], or None if unknown (default: None).
        voltage : float or None, optional
            The voltage measured in [mV], or None if unknown (default: None).
        comment : str, optional
            Additional comment about the measurement (default: "").

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If empty string for `object_id`.
            If negative value for `rod_length`.
        """

        # Initialize all attributes using private setters.
        self._set_project(project)
        self._set_device(device)
        self._set_object_id(object_id)
        self._set_date_time(date_time)
        self._set_coordinate_reference_system(coordinate_reference_system)
        self._set_x(x)
        self._set_y(y)
        self._set_z(z)
        self._set_rod_length(rod_length)
        self._set_plate_bottom_z(plate_bottom_z)
        self._set_ground_surface_z(ground_surface_z)
        self._set_status(status)
        self._set_temperature(temperature)
        self._set_voltage(voltage)
        self._set_comment(comment)

    def _set_project(self, value: Project) -> None:
        """
        Private setter for project attribute.
        """
        if not isinstance(value, Project):
            raise TypeError("Expected 'Project' type for 'project' attribute.")
        self._project = value

    def _set_device(self, value: MeasurementDevice) -> None:
        """
        Private setter for device attribute.
        """
        if not isinstance(value, MeasurementDevice):
            raise TypeError("Expected 'MeasurementDevice' type for 'device' attribute.")
        self._device = value

    def _set_object_id(self, value: str) -> None:
        """
        Private setter for object_id attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'object_id' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'object_id' attribute.")
        self._object_id = value

    def _set_date_time(self, value: datetime.datetime) -> None:
        """
        Private setter for date_time attribute.
        """
        if not isinstance(value, datetime.datetime):
            raise TypeError(
                "Expected 'datetime.datetime' type for 'date_time' attribute."
            )
        self._date_time = value

    def _set_coordinate_reference_system(self, value: pyproj.CRS) -> None:
        """
        Private setter for coordinate_reference_system attribute.
        """
        if not isinstance(value, pyproj.CRS):
            raise TypeError(
                "Expected 'pyproj.CRS' type for 'coordinate_reference_system' attribute."
            )
        self._coordinate_reference_system = value

    def _set_x(self, value: float) -> None:
        """
        Private setter for x attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'x' attribute.")
        self._x = value

    def _set_y(self, value: float) -> None:
        """
        Private setter for y attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type 'y' attribute.")
        self._y = value

    def _set_z(self, value: float) -> None:
        """
        Private setter for z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'z' attribute.")
        self._z = value

    def _set_rod_length(self, value: float) -> None:
        """
        Private setter for rod_length attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'rod_length' attribute.")
        if value < 0:
            raise ValueError("Negative value not allowed for 'rod_length' attribute.")
        self._rod_length = value

    def _set_plate_bottom_z(self, value: float) -> None:
        """
        Private setter for plate_bottom_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'plate_bottom_z' attribute.")
        self._plate_bottom_z = value

    def _set_ground_surface_z(self, value: float) -> None:
        """
        Private setter for ground_surface_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'ground_surface_z' attribute.")
        self._ground_surface_z = value

    def _set_status(self, value: SettlementRodMeasurementStatus) -> None:
        """
        Private setter for status attribute.
        """
        if not isinstance(value, SettlementRodMeasurementStatus):
            raise TypeError(
                "Expected 'SettlementRodMeasurementStatus' type for 'status' attribute."
            )
        self._status = value

    def _set_temperature(self, value: float | None) -> None:
        """
        Private setter for temperature attribute.
        """
        if value is not None:
            if isinstance(value, int):
                value = float(value)
            if not isinstance(value, float):
                raise TypeError(
                    "Expected 'float' or 'None' type for 'temperature' attribute."
                )
        self._temperature = value

    def _set_voltage(self, value: float | None) -> None:
        """
        Private setter for voltage attribute.
        """
        if value is not None:
            if isinstance(value, int):
                value = float(value)
            if not isinstance(value, float):
                raise TypeError(
                    "Expected 'float' or 'None' type for 'voltage' attribute."
                )
        self._voltage = value

    def _set_comment(self, value: str) -> None:
        """
        Private setter for comment attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'comment' attribute.")
        self._comment = value

    @property
    def project(self) -> Project:
        """
        The project which the measurement belongs to.
        """
        return self._project

    @property
    def device(self) -> MeasurementDevice:
        """
        The measurement device.
        """
        return self._device

    @property
    def object_id(self) -> str:
        """
        The ID of the measured object.
        """
        return self._object_id

    @property
    def date_time(self) -> datetime.datetime:
        """
        The date and time of the measurement.
        """
        return self._date_time

    @property
    def coordinate_reference_system(self) -> pyproj.CRS:
        """
        The coordinate reference system of the spatial measurements.
        It is a `pyproj.CRS` object (see https://pyproj4.github.io/pyproj/stable/api/crs/crs.html).
        """
        return self._coordinate_reference_system

    @property
    def x(self) -> float:
        """
        The X-coordinate of the measurement point.
        Units are according to the `coordinate_reference_system`.
        """
        return self._x

    @property
    def y(self) -> float:
        """
        The Y-coordinate of the measurement point.
        Units are according to the `coordinate_reference_system`.
        """
        return self._y

    @property
    def z(self) -> float:
        """
        The Z-coordinate of the measurement point.
        It is the top of the settlement rod.
        Units are according to the `coordinate_reference_system`.
        """
        return self._z

    @property
    def rod_length(self) -> float:
        """
        The length of the settlement rod including the thickness of the settlement plate.
        It is in principle the vertical distance between the measurement point and the bottom of the settlement plate.
        Units are according to the `coordinate_reference_system`.
        """
        return self._rod_length

    @property
    def plate_bottom_z(self) -> float:
        """
        The corrected Z-coordinate at the bottom of the settlement plate.
        Note that the bottom of the plate is in principle the original ground surface.
        Units are according to the `coordinate_reference_system`.
        """
        return self._plate_bottom_z

    @property
    def plate_bottom_z_uncorrected(self) -> float:
        """
        The uncorrected Z-coordinate at the bottom of the settlement plate.
        It is computed as the difference beteen the Z-coordinate of the measurement point and the vertical offset.
        Units are according to the `coordinate_reference_system`.
        """
        return self.z - self.rod_length

    @property
    def ground_surface_z(self) -> float:
        """
        The Z-coordinate of the ground surface.
        It is in principle the top of the fill, if present.
        """
        return self._ground_surface_z

    @property
    def status(self) -> SettlementRodMeasurementStatus:
        """
        The status of the measurement.
        """
        return self._status

    @property
    def temperature(self) -> float | None:
        """
        The temperature at the time of measurement in [°C], or None if unknown.
        """
        return self._temperature

    @property
    def voltage(self) -> float | None:
        """
        The voltage measured in [mV], or None if unknown.
        """
        return self._voltage

    @property
    def comment(self) -> str:
        """
        Additional comment about the measurement.
        """
        return self._comment
