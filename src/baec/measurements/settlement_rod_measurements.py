from __future__ import annotations

import datetime

import pyproj


class SettlementRodMeasurement:
    """
    Represents a single settlement rod measurement.
    """

    def __init__(
        self,
        date_time: datetime.datetime,
        rod_id: str,
        point_id: str,
        coordinate_epsg_code: int,
        x: float,
        y: float,
        z: float,
        vertical_offset: float,
        plate_bottom_z: float,
        ground_surface_z: float | None = None,
        temperature: float | None = None,
        voltage: float | None = None,
        comment: str = "No comment",
    ) -> None:
        """
        Initializes a SettlementRodMeasurement object.

        Parameters
        ----------
        date_time : datetime.datetime
            The date and time of the measurement.
        rod_id : str
            The ID of the settlement rod.
        point_id : str
            The ID of the measurement point.
        coordinate_epsg_code : int
            The EPSG code of the coordinate reference system used.
            EPSG codes can be found in https://epsg.io/.
        x : float
            The X-coordinate of the measurement point. Units are according to the `coordinate_reference_system`.
        y : float
            The Y-coordinate of the measurement point. Units are according to the `coordinate_reference_system`.
        z : float
            The Z-coordinate of the measurement point.
            It is the top of the settlement rod.
            Units are according to the `coordinate_reference_system`.
        vertical_offset : float
            The vertical offset distance between the measurement point and the bottom of the settlement plate.
            It is in principle the rod length plus the plate thickness.
            Units are according to the `coordinate_reference_system`.
        plate_bottom_z : float
            The corrected Z-coordinate at the bottom of the settlement plate.
            Note that the bottom of the plate is in principle the original ground surface.
            Units are according to the `coordinate_reference_system`.
        ground_surface_z : float | None, optional
            The Z-coordinate of the ground surface, or None if unknown (default: None).
            Notes:
                - This value in principle corresponds to the top of the fill, if present.
                - This value will be typically measured using radar measurements.
            Units are according to the `coordinate_reference_system`.
        temperature : float or None, optional
            The temperature at the time of measurement in [°C], or None if unknown (default: None).
        voltage : float or None, optional
            The voltage measured in [mV], or None if unknown (default: None).
        comment : str, optional
            Comment about the measurement (default: "No comment").

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If empty string for `rod_id` or `point_id`.
        ValueError
            If negative value for `coordinate_epsg_code` or `vertical_offset`.
        pyproj.exceptions.CRSError
            If no valid coordinate reference system is found for the given `coordinate_epsg_code`.
        """

        # Initialize all attributes using private setters.
        self._set_date_time(date_time)
        self._set_rod_id(rod_id)
        self._set_point_id(point_id)
        self._set_coordinate_epsg_code(coordinate_epsg_code)
        self._set_x(x)
        self._set_y(y)
        self._set_z(z)
        self._set_vertical_offset(vertical_offset)
        self._set_plate_bottom_z(plate_bottom_z)
        self._set_ground_surface_z(ground_surface_z)
        self._set_temperature(temperature)
        self._set_voltage(voltage)
        self._set_comment(comment)

        # Set the coordinate reference system based on the EPSG code
        self._coordinate_reference_system = pyproj.CRS.from_user_input(
            coordinate_epsg_code
        )

    def _set_date_time(self, value: datetime.datetime) -> None:
        """
        Private setter for date attribute.
        """
        if not isinstance(value, datetime.datetime):
            raise TypeError("Expected 'datetime.datetime' type for 'date' attribute.")
        self._date_time = value

    def _set_rod_id(self, value: str) -> None:
        """
        Private setter for rod_id attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'rod_id' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'rod_id' attribute.")
        self._rod_id = value

    def _set_point_id(self, value: str) -> None:
        """
        Private setter for point_id attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'point_id' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'point_id' attribute.")
        self._point_id = value

    def _set_coordinate_epsg_code(self, value: int) -> None:
        """
        Private setter for coordinate_epsg_code attribute.
        """
        if not isinstance(value, int):
            raise TypeError("Expected 'int' type for 'coordinate_epsg_code' attribute.")
        if value < 0:
            raise ValueError(
                "Negative value not allowed for 'coordinate_epsg_code' attribute."
            )
        self._coordinate_epsg_code = value

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

    def _set_vertical_offset(self, value: float) -> None:
        """
        Private setter for vertical_offset attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'vertical_offset' attribute.")
        if value < 0:
            raise ValueError(
                "Negative value not allowed for 'vertical_offset' attribute."
            )
        self._vertical_offset = value

    def _set_plate_bottom_z(self, value: float) -> None:
        """
        Private setter for plate_bottom_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'plate_bottom_z' attribute.")
        self._plate_bottom_z = value

    def _set_ground_surface_z(self, value: float | None) -> None:
        """
        Private setter for ground_surface_z attribute.
        """
        if value is not None:
            if isinstance(value, int):
                value = float(value)
            if not isinstance(value, float):
                raise TypeError(
                    "Expected 'float' or 'None' type for 'ground_surface_z' attribute."
                )
        self._ground_surface_z = value

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
    def date_time(self) -> datetime.datetime:
        """
        The date and time of the measurement.
        """
        return self._date_time

    @property
    def rod_id(self) -> str:
        """
        The ID of the settlement rod.
        """
        return self._rod_id

    @property
    def point_id(self) -> str:
        """
        The ID of the measurement point.
        """
        return self._point_id

    @property
    def coordinate_epsg_code(self) -> int:
        """
        The EPSG code of the coordinate reference system used.
        EPSG codes can be found in https://epsg.io/.
        """
        return self._coordinate_epsg_code

    @property
    def coordinate_reference_system(self) -> pyproj.CRS:
        """
        The coordinate reference system used.
        It is a `pyproj.CRS` object (see https://pyproj4.github.io/pyproj/stable/api/crs/crs.html).
        It is determined based on the `coordinate_epsg_code`.
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
    def vertical_offset(self) -> float:
        """
        The vertical offset distance between the measurement point and the bottom of the settlement plate.
        It is in principle the rod length plus the plate thickness.
        Units are according to the `coordinate_reference_system`.
        """
        return self._vertical_offset

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
        return self.z - self.vertical_offset

    @property
    def ground_surface_z(self) -> float | None:
        """
        The Z-coordinate of the ground surface, or None if unknown.
        """
        return self._ground_surface_z

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
        Comment about the measurement.
        """
        return self._comment
