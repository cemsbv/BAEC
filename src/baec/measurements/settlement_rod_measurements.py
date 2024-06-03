from __future__ import annotations

import datetime

import pyproj


class SettlementRodMeasurement:
    """
    Represents the measurement of a settlement rod.

    Attributes
    ----------
    date_time : datetime.datetime
        The date and time of the measurement.
    rod_id : str
        The ID of the settlement rod.
    point_id : str
        The ID of the measurement point.
    coordinate_epsg_code : int
        The EPSG code of the coordinate reference system used.
        EPSG codes can be found in https://epsg.io/ .
    point_x : float
        The X-coordinate of the measurement point.
    point_y : float
        The Y-coordinate of the measurement point.
    point_z : float
        The Z-coordinate of the measurement point.
        It is the top of the settlement rod.
    rod_length : float
        The length of the settlement rod.
        Note that the settlement rod connects the measurement point with the ground plate,
        thus this value is in principle the vertical distance between these two points.
    ground_plate_z : float
        The corrected Z-coordinate of the ground plate.
        Note that this plate is in contact with the original ground surface.
    ground_surface_z : float | None, optional
        The Z-coordinate of the ground surface, or None if unknown (default: None).
        Notes:
            - This value in principle corresponds to the top of the fill, if present.
            - This value will be typically measured using radar measurements.
    temperature : float or None, optional
        The temperature at the time of measurement in [°C], or None if unknown (default: None).
    voltage : float or None, optional
        The voltage measured in [mV], or None if unknown (default: None).
    comment : str, optional
        Additional comment about the measurement (default: "No comment").

    Properties
    ----------
    coordinate_reference_system : pyproj.CRS
        The coordinate reference system used.
    ground_plate_z_uncorrected : float
        The uncorrected Z-coordinate of the ground plate.
        Computed as the difference between point_z and rod_length.
    """

    def __init__(
        self,
        date_time: datetime.datetime,
        rod_id: str,
        point_id: str,
        coordinate_epsg_code: int,
        point_x: float,
        point_y: float,
        point_z: float,
        rod_length: float,
        ground_plate_z: float,
        ground_surface_z: float,
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
            EPSG codes can be found in https://epsg.io/ .
        point_x : float
            The X-coordinate of the measurement point.
        point_y : float
            The Y-coordinate of the measurement point.
        point_z : float
            The Z-coordinate of the measurement point.
            It is the top of the settlement rod.
        rod_length : float
            The length of the settlement rod.
            Note that the settlement rod connects the measurement point with the ground plate,
            thus this value is in principle the vertical distance between these two points.
        ground_plate_z : float
            The corrected Z-coordinate of the ground plate.
            Note that this plate is in contact with the original ground surface.
        ground_surface_z : float | None, optional
        The Z-coordinate of the ground surface, or None if unknown (default: None).
        Notes:
            - This value in principle corresponds to the top of the fill, if present.
            - This value will be typically measured using radar measurements.
        temperature : float or None, optional
            The temperature at the time of measurement in [°C], or None if unknown (default: None).
        voltage : float or None, optional
            The voltage measured in [mV], or None if unknown (default: None).
        comment : str, optional
            Additional comment about the measurement (default: "No comment").

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            - If empty string for `rod_id` or `point_id`.
            - If negative value for `coordinate_epsg_code` or `rod_length`.
        pyproj.exceptions.CRSError
            If no valid coordinate reference system is found for the given EPSG code.
        """

        # Initialize all attributes using private setters.
        self._set_date_time(date_time)
        self._set_rod_id(rod_id)
        self._set_point_id(point_id)
        self._set_coordinate_epsg_code(coordinate_epsg_code)
        self._set_point_x(point_x)
        self._set_point_y(point_y)
        self._set_point_z(point_z)
        self._set_rod_length(rod_length)
        self._set_ground_plate_z(ground_plate_z)
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

    def _set_point_x(self, value: float) -> None:
        """
        Private setter for point_x attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'point_x' attribute.")
        self._point_x = value

    def _set_point_y(self, value: float) -> None:
        """
        Private setter for point_y attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'point_y' attribute.")
        self._point_y = value

    def _set_point_z(self, value: float) -> None:
        """
        Private setter for point_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'point_z' attribute.")
        self._point_z = value

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

    def _set_ground_surface_z(self, value: float) -> None:
        """
        Private setter for ground_surface_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'ground_surface_z' attribute.")
        self._ground_surface_z = value

    def _set_ground_plate_z(self, value: float) -> None:
        """
        Private setter for ground_plate_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'ground_plate_z' attribute.")
        self._ground_plate_z = value

    def _set_ground_plate_z_uncorrected(self, value: float) -> None:
        """
        Private setter for ground_plate_z_uncorrected attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError(
                "Expected 'float' type for 'ground_plate_z_uncorrected' attribute."
            )
        self._ground_plate_z_uncorrected = value

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
        EPSG codes can be found in https://epsg.io/ .
        """
        return self._coordinate_epsg_code

    @property
    def coordinate_reference_system(self) -> pyproj.CRS:
        """
        The coordinate reference system used.
        """
        return self._coordinate_reference_system

    @property
    def point_x(self) -> float:
        """
        The X-coordinate of the measurement point.
        """
        return self._point_x

    @property
    def point_y(self) -> float:
        """
        The Y-coordinate of the measurement point.
        """
        return self._point_y

    @property
    def point_z(self) -> float:
        """
        The Z-coordinate of the measurement point.
        """
        return self._point_z

    @property
    def rod_length(self) -> float:
        """
        The length of the settlement rod.
        """
        return self._rod_length

    @property
    def ground_plate_z(self) -> float:
        """
        The corrected Z-coordinate of the ground plate.
        """
        return self._ground_plate_z

    @property
    def ground_plate_z_uncorrected(self) -> float:
        """
        The uncorrected Z-coordinate of the ground plate.
        """
        return self.point_z - self.rod_length

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
        Additional comment about the measurement.
        """
        return self._comment
