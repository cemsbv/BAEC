from __future__ import annotations

import datetime
from functools import cache, wraps
from typing import Any, Callable, Dict, List, Literal, Tuple

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter

from baec.measurements.measured_settlement import MeasuredSettlement
from baec.measurements.settlement_rod_measurement import SettlementRodMeasurementStatus
from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)
from baec.project import Project


def add_docstring_plot_time(return_type: Literal["axes", "figure"]) -> Callable:
    """
    Decorator to add the docstring of the plot methods over time for the MeasuredSettlementSeries class.
    """
    assert return_type in [
        "axes",
        "figure",
    ], "Expected 'axes' or 'figure' for 'return_type' parameter."

    docstring_plot_time = """
        Parameters
        ----------
        axes: plt.Axes | None, optional
            Axes to create the figure. If None creates new Axes.
            Default is None.
        log_time: bool, optional
            If True, the time axis is logarithmic (linear otherwise).
            Note that time is plotted in days.
            Default is True.
        min_log_time: float, optional
            The minimum value for the time axis in [days] in case of a logarithmic plot.
            It must be greater than 0.0.
            Default is 1.0.
        add_date_time: bool, optional
            If True, the date and time are added as a secondary x-axis.
            Default is True.
        datetime_format: str, optional
            The format of the date and time on the x-axis (only used if `add_date_time` is True).
            It must be an acceptable format for the strftime method of the datetime.datetime class.
            Default is "%d-%m-%Y".

        Returns
        -------
        plt.Axes

        Raises
        ------
        TypeError
            If the types of the input parameters are incorrect.
        ValueError
            If the `datetime_format` is not a valid format for the strftime method of the
            datetime.datetime class.
            If the `min_log_time` is not greater than 0.0.
        """

    if return_type == "figure":
        docstring_plot_time = docstring_plot_time.replace(
            """
        axes: plt.Axes | None, optional
            Axes to create the figure. If None creates new Axes.
            Default is None.""",
            "",
        )
        docstring_plot_time = docstring_plot_time.replace("plt.Axes", "plt.Figure")

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: Any, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Callable:
            return func(self, *args, **kwargs)

        if func.__doc__ is None:
            func.__doc__ = ""

        wrapper.__doc__ = func.__doc__ + docstring_plot_time

        return wrapper

    return decorator


class MeasuredSettlementSeries:
    """
    Represents a series of MeasuredSettlement objects, derived for a single settlement rod.
    """

    def __init__(self, items: List[MeasuredSettlement]) -> None:
        """
        Initializes a MeasuredSettlementSeries object.

        Parameters
        ----------
        items : List[MeasuredSettlement]
            The list of MeasuredSettlement objects.

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If the list of measurements is empty.
            If the measurements are not for the same project, object, horizontal or
            vertical units.
        """

        # Initialize all attributes using private setters.
        self._set_items(items)

        # Set properties common to all measured settlements
        self._project = self.items[0].project
        self._object_id = self.items[0].object_id
        self._start_date_time = self.items[0].start_date_time
        self._horizontal_units = self.items[0].horizontal_units
        self._vertical_units = self.items[0].vertical_units

        # Set properties that are lists
        self._date_times = []
        self._days = []
        self._fill_thicknesses = []
        self._settlements = []
        self._x_displacements = []
        self._y_displacements = []
        self._statuses = []
        for item in self.items:
            self._date_times.append(item.date_time)
            self._days.append(item.days)
            self._fill_thicknesses.append(item.fill_thickness)
            self._settlements.append(item.settlement)
            self._x_displacements.append(item.x_displacement)
            self._y_displacements.append(item.y_displacement)
            self._statuses.append(item.status)

    @classmethod
    def from_settlement_rod_measurement_series(
        cls,
        series: SettlementRodMeasurementSeries,
        start_index: int | None = None,
        start_date_time: datetime.datetime | None = None,
    ) -> MeasuredSettlementSeries:
        """
        Create a MeasuredSettlementSeries object from a SettlementRodMeasurementSeries object.

        The `start_index` and `start_date_time` are used to determine the start (or zero measurement)
        from the series of measurements. The following rules are applied:
        1. Either `start_index` or `start_date_time` can be provided. If both are provided, an error
        is raised.
        2. If neither `start_index` not `start_date_time` are provided, the first measurement or the
        series in used as the zero measurement. This is the default behaviour.
        3. If `start_index` is provided, the measurement at the index is used the zero measurement.
        4. If `start_date_time` is provided, the first measurement equal or after this date and time is
        considered as the zero measurement.

        Parameters
        ----------
        series : SettlementRodMeasurementSeries
            The series of SettlementRodMeasurement objects.
        start_index: int | None, optional
            The index of the item of the series to consider as the start or zero measurement of the series, or None.
            Default is None.
        start_date_time: int | None, optional
            The date at which the start or zero measurement is taken place, or None.
            Default is None.

        Returns
        -------
        MeasuredSettlementSeries

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If both `start_index` and `start_date_time` are provided.
            If the `start_date_time` is out of range for the series.
        IndexError
            If the `start_index` is out of range for the series.
        """
        # Check the types of the input parameters.
        if not isinstance(series, SettlementRodMeasurementSeries):
            raise TypeError(
                "Expected 'SettlementRodMeasurementSeries' type for 'series' parameter."
            )

        if start_index is not None and not isinstance(start_index, int):
            raise TypeError("Expected 'int' type or None for 'start_index' parameter.")

        if start_date_time is not None and not isinstance(
            start_date_time, datetime.datetime
        ):
            raise TypeError(
                "Expected 'datetime.datetime' type or None for 'start_date_time' parameter."
            )

        # Check that either start_index or start_date_time is None.
        if start_index is not None and start_date_time is not None:
            raise ValueError(
                "Only one of 'start_index' or 'start_date_time' can be provided."
            )

        # Check that the start_index is within the range of the series.
        if start_index is not None:
            try:
                series.measurements[start_index]
            except IndexError:
                raise IndexError(
                    f"start_index = {start_index} is out of range for the series. Length of series "
                    + f"is {len(series.measurements)}."
                )

        # Check that the start_date_time is within the range of the series.
        if (
            start_date_time is not None
            and not series.measurements[0].date_time
            <= start_date_time
            <= series.measurements[-1].date_time
        ):
            raise ValueError(
                f"start_date_time = {start_date_time} is out of range for the series. "
                + f"Valid range is {series.measurements[0].date_time} to "
                + f"{series.measurements[-1].date_time}."
            )

        # Get start index from the start_date_time.
        if start_index is None:
            if start_date_time is not None:
                for start_index, measurement in enumerate(series.measurements):
                    if measurement.date_time >= start_date_time:
                        break
            # Else, both the start_index and start_date_time are None and thus
            # the start index is set to 0.
            else:
                start_index = 0

        # Create a list of MeasuredSettlement objects from the series of measurements.
        measured_settlements = []
        for measurement in series.measurements[start_index:]:
            measured_settlements.append(
                MeasuredSettlement.from_settlement_rod_measurement(
                    measurement=measurement,
                    zero_measurement=series.measurements[start_index],
                )
            )

        return cls(measured_settlements)

    def _set_items(self, value: List[MeasuredSettlement]) -> None:
        """Private setter for items attribute."""

        # Check if the input is a list of SettlementRodMeasurement objects.
        if not all(isinstance(item, MeasuredSettlement) for item in value):
            raise TypeError(
                "Expected 'List[MeasuredSettlement]' type for 'items' attribute."
            )

        # Check if the list is not empty.
        if not value:
            raise ValueError("Empty list not allowed for 'items' attribute.")

        # Check that the items are for the same project.
        projects = []
        for measurement in value:
            if measurement.project not in projects:
                projects.append(measurement.project)
        if len(projects) > 1:
            raise ValueError(
                "All items must be for the same project. "
                + f"The following projects are found: {projects}"
            )

        # Check that the items are for the same object.
        object_ids = []
        for measurement in value:
            if measurement.object_id not in object_ids:
                object_ids.append(measurement.object_id)
        if len(object_ids) > 1:
            raise ValueError(
                "All items must be for the same measured object. "
                + f"The following object IDs are found: {object_ids}"
            )

        # Check that the items have the same start_date_time.
        start_date_times = []
        for measurement in value:
            if measurement.start_date_time not in start_date_times:
                start_date_times.append(measurement.start_date_time)
        if len(start_date_times) > 1:
            raise ValueError(
                "All items must have the same start date time. "
                + f"The following start date times are found: {start_date_times}"
            )

        # Check that the items have all the same horizontal units.
        horizontal_units_list = []
        for measurement in value:
            if measurement.horizontal_units not in horizontal_units_list:
                horizontal_units_list.append(measurement.horizontal_units)
        if len(horizontal_units_list) > 1:
            raise ValueError(
                "All items must have the same horizontal units. "
                + f"The following horizontal units are found: {horizontal_units_list}"
            )

        # Check that the items have all the same vertical units.
        vertical_units_list = []
        for measurement in value:
            if measurement.vertical_units not in vertical_units_list:
                vertical_units_list.append(measurement.vertical_units)
        if len(vertical_units_list) > 1:
            raise ValueError(
                "All items must be in the same vertical units. "
                + f"The following vertical units are found: {vertical_units_list}"
            )

        # Organize the list of MeasureSettlement objects in chronological order.
        self._items = sorted(value, key=lambda x: x.date_time)

    @property
    def items(self) -> List[MeasuredSettlement]:
        """
        The list of measured settlements in the series.
        They are organized in chronological order.
        """
        return self._items

    @property
    def project(self) -> Project:
        """
        The project the measured settlements belong to.
        """
        return self._project

    @property
    def object_id(self) -> str:
        """
        The ID of the object the measured settlements belong to.
        """
        return self._object_id

    @property
    def start_date_time(self) -> datetime.datetime:
        """
        The date and time of the start of measurements (zero measurement).
        """
        return self._start_date_time

    @property
    def horizontal_units(self) -> str:
        """
        The units of the horizontal XY displacements of the measured settlements.
        """
        return self._horizontal_units

    @property
    def vertical_units(self) -> str:
        """
        The units of the measurements and distances in the vertical direction
        of the measured settlements.
        """
        return self._vertical_units

    @property
    def date_times(self) -> List[datetime.datetime]:
        """
        The list of date and times for each measured settlement.
        """
        return self._date_times

    @property
    def days(self) -> List[float]:
        """
        The list of time elapsed in [days] since the start of measurements
        for each measured settlement.
        """
        return self._days

    @property
    def fill_thicknesses(self) -> List[float]:
        """
        The list of fill thicknesses for each measured settlement.
        Units are according to `vertical_units`.
        """
        return self._fill_thicknesses

    @property
    def settlements(self) -> List[float]:
        """
        The list of settlements of the initial ground profile relative to the zero measurement.
        A positive (+) settlement value represents a downward movement.
        Units are according to `vertical_units`.
        """
        return self._settlements

    @property
    def x_displacements(self) -> List[float]:
        """
        The list of horizontal X-displacements at the rod top relative to the zero measurement.
        Units are according to the `horizontal_units`.
        """
        return self._x_displacements

    @property
    def y_displacements(self) -> List[float]:
        """
        The list of horizontal Y-displacements at the rod top relative to the zero measurement.
        Units are according to the `horizontal_units`.
        """
        return self._y_displacements

    @property
    def statuses(self) -> List[SettlementRodMeasurementStatus]:
        """
        The list of status objects of the settlement rod measurement from which the measured settlement
        is derived.
        """
        return self._statuses

    @cache
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the MeasuredSettlementSeries to a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with the measured settlements. The columns of the DataFrame are:
            project_id, project_name, object_id, start_date_time
            date_time, days, fill_thickness, settlement, x_displacement, y_displacement
            horizontal_units, vertical_units, status
        """
        return pd.DataFrame.from_records(
            [measurement.to_dict() for measurement in self.items]
        )

    def days_to_date_time(self, days: float) -> datetime.datetime:
        """
        Convert the days since the start of the measurements to a date and time.
        Note that the days can be a decimal.

        Parameters
        ----------
        days : float
            The days since the start of the measurements.

        Returns
        -------
        datetime.datetime
            The date and time corresponding to days since the start of measurements.
        """
        # Check that days is float or int
        if not isinstance(days, (float, int)):
            raise TypeError("Expected 'float' type for 'days' parameter.")

        return self.start_date_time + datetime.timedelta(days=days)

    def date_time_to_days(self, date_time: datetime.datetime) -> float:
        """
        Convert the date time to days since the start of measurements.

        Parameters
        ----------
        date_time : datetime.datetime
            The date and time to convert to days since the start of measurements.

        Returns
        -------
        float
            The days since the start of the measurements. Note that the days can be a decimal.
        """
        # Check that date_time is datetime.datetime
        if not isinstance(date_time, (datetime.datetime)):
            raise TypeError(
                f"Expected 'date_time.date_time' type for 'date_time' parameter, but got {type(date_time)}."
            )
        return (date_time - self.start_date_time).total_seconds() / 86400.0

    @add_docstring_plot_time(return_type="axes")
    def plot_x_displacement_time(
        self,
        axes: Axes | None = None,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
    ) -> Axes:
        """
        Plot the horizontal X displacement at the top of the rod relative to the
        zero measurement over time.
        """
        return self._plot_property_time(
            property="x_displacements",
            axes=axes,
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=add_date_time,
            datetime_format=datetime_format,
        )

    @add_docstring_plot_time(return_type="axes")
    def plot_y_displacement_time(
        self,
        axes: Axes | None = None,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
    ) -> Axes:
        """
        Plot the horizontal Y displacement at the top of the rod relative to the
        zero measurement over time.
        """
        return self._plot_property_time(
            property="y_displacements",
            axes=axes,
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=add_date_time,
            datetime_format=datetime_format,
        )

    @add_docstring_plot_time(return_type="axes")
    def plot_settlement_time(
        self,
        axes: Axes | None = None,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
    ) -> Axes:
        """
        Plot the settlement of the initial ground profile rod over time.
        """
        return self._plot_property_time(
            property="settlements",
            axes=axes,
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=add_date_time,
            datetime_format=datetime_format,
        )

    @add_docstring_plot_time(return_type="axes")
    def plot_fill_time(
        self,
        axes: Axes | None = None,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
    ) -> Axes:
        """
        Plot the fill thickness over time.
        """
        return self._plot_property_time(
            property="fill_thicknesses",
            axes=axes,
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=add_date_time,
            datetime_format=datetime_format,
        )

    @add_docstring_plot_time(return_type="figure")
    def plot_fill_settlement_time(
        self,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
    ) -> Figure:
        """
        Plot in a new fill thickness and the settlement of the initial ground profile
        relative to the zero measurement over time.
        """
        fig, axes = plt.subplots(2, 1, figsize=(10, 20), sharex=True)

        self.plot_fill_time(
            axes=axes[0],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=add_date_time,
            datetime_format=datetime_format,
        )
        axes[0].set_title("")
        axes[0].set_xlabel("")

        self.plot_settlement_time(
            axes=axes[1],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=False,
            datetime_format=datetime_format,
        )
        axes[1].set_title("")

        if add_date_time:
            fig.subplots_adjust(top=0.825, hspace=0.075)

        fig.suptitle(f"Fill thickness and settlement for object: {self.object_id}")

        return fig

    @add_docstring_plot_time(return_type="figure")
    def plot_displacements_time(
        self,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
    ) -> Figure:
        """
        Plot in a new figure the horizontal XY-displacements at the top of rod and the
        fill thickness and the settlement of the initial ground profile relative to the
        zero measurement over time.
        """
        fig, axes = plt.subplots(4, 1, figsize=(10, 40), sharex=True)

        self.plot_x_displacement_time(
            axes=axes[0],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=add_date_time,
            datetime_format=datetime_format,
        )
        axes[0].set_title("")
        axes[0].set_xlabel("")

        self.plot_y_displacement_time(
            axes=axes[1],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=False,
            datetime_format=datetime_format,
        )
        axes[1].set_title("")
        axes[1].set_xlabel("")

        self.plot_fill_time(
            axes=axes[2],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=False,
            datetime_format=datetime_format,
        )
        axes[2].set_title("")
        axes[2].set_xlabel("")

        self.plot_settlement_time(
            axes=axes[3],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=False,
            datetime_format=datetime_format,
        )
        axes[3].set_title("")

        if add_date_time:
            fig.subplots_adjust(top=0.825, hspace=0.1)

        fig.suptitle(f"Fill and displacements for object: {self.object_id}")

        return fig

    def plot_xy_displacements_plan_view(self, axes: Axes | None = None) -> Axes:
        """
        Plot the plan view of the horizontal XY displacements
        at the top of the rod, relative to the zero measurement.

        Parameters
        ----------
        axes: plt.Axes | None, optional
            Axes to create the figure. If None, then create new Axes.
            Default is None.

        Returns
        -------
        plt.Axes
        """
        self._validate_plot_parameter_axes(axes)

        # If axes is None create new Axes.
        if axes is None:
            plt.figure()
            axes = plt.gca()

        # Plot the X and Y displacements
        axes.plot(self.x_displacements, self.y_displacements)

        # Mark the start and end of the measurements.
        axes.plot(
            self.x_displacements[0],
            self.y_displacements[0],
            marker="*",
            color="black",
            label="start",
        )

        axes.plot(
            self.x_displacements[-1],
            self.y_displacements[-1],
            marker="+",
            color="red",
            label="end",
        )

        axes.legend(loc="upper right")

        abs_max = max(
            -min(self.x_displacements),
            max(self.x_displacements),
            -min(self.y_displacements),
            max(self.y_displacements),
        )
        axes.set_xlim(-abs_max - 0.5, abs_max + 0.5)
        axes.set_ylim(-abs_max - 0.5, abs_max + 0.5)

        axes.set_aspect("equal")
        axes.grid()

        axes.set_xlabel(f"X [{self.horizontal_units}]")
        axes.set_ylabel(f"Y [{self.horizontal_units}]")
        axes.set_title(
            f"Plan view of horizonal measurements at rod top for object: {self.object_id}"
        )

        return axes

    @add_docstring_plot_time(return_type="axes")
    def _plot_property_time(
        self,
        property: Literal[
            "fill_thicknesses",
            "settlements",
            "x_displacements",
            "y_displacements",
        ],
        axes: Axes | None = None,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
    ) -> Axes:
        """
        Private method to plot the requested property over time.
        """
        # Assert the requested property is one accepted one.
        assert property in [
            "fill_thicknesses",
            "settlements",
            "x_displacements",
            "y_displacements",
        ], "Expected 'fill_thicknesses', 'settlements', 'x_displacements' or 'y_displacements' for 'property' parameter."

        # Validate input plot parameters
        self._validate_plot_parameter_axes(axes)
        self._validate_plot_parameter_log_time(log_time)
        self._validate_plot_parameter_min_log_time(min_log_time)
        self._validate_plot_parameter_add_date_time(add_date_time)
        self._validate_plot_parameter_datetime_format(datetime_format)

        # Map y_label, titles and units per property
        y_labels = {
            "fill_thicknesses": "Fill thickness",
            "settlements": "Settlement",
            "x_displacements": "X displacement",
            "y_displacements": "Y displacement",
        }

        titles = {
            "fill_thicknesses": "Fill thickness",
            "settlements": "Settlement of initial ground surface",
            "x_displacements": "Horizontal X displacement at rod top",
            "y_displacements": "Horizontal Y displacement at rod top",
        }

        units = {
            "fill_thicknesses": self.vertical_units,
            "settlements": self.vertical_units,
            "x_displacements": self.horizontal_units,
            "y_displacements": self.horizontal_units,
        }

        # If axes is None create new Axes.
        if axes is None:
            plt.figure()
            axes = plt.gca()

        # Plot the property data over time
        axes.plot(self.days, getattr(self, property))

        if log_time:
            axes.set_xlim(min_log_time, max(self.days) + 1.0)
            axes.set_xscale("log")

        axes.set_ylim(
            min(getattr(self, property)) - 0.5, max(getattr(self, property)) + 0.5
        )
        if property == "settlements":
            axes.invert_yaxis()

        axes.xaxis.set_major_formatter(ScalarFormatter())
        axes.xaxis.set_minor_formatter(ScalarFormatter())
        axes.grid(which="both")

        axes.set_ylabel(f"{y_labels[property]} [{units[property]}]")
        axes.set_xlabel("Time [days]")
        axes.set_title(f"{titles[property]} for object: {self.object_id}")

        # Add secondary xaxis with the date_time
        if add_date_time:
            axes = self._add_datetime_as_secondary_axis(
                axes=axes, datetime_format=datetime_format
            )

        return axes

    def _add_datetime_as_secondary_axis(
        self,
        axes: Axes,
        datetime_format: str = "%d-%m-%Y",
    ) -> Axes:
        """
        Private helper method to add a secondary x-axis to the provided `axes` with the date and time
        data. The original x-axis is expected to be time in [days].

        Parameters
        ----------
        axes: plt.Axes
            Axes to create the figure
        datetime_format: str, optional
            The format of the date and time on the x-axis.
            It must be an acceptable format for the strftime method of the datetime.datetime class.
            Default is "%d-%m-%Y".

        Returns
        -------
        plt.Axes

        Raises
        ------
        TypeError
            If the types of the input parameters are incorrect.
        ValueError
            If the `datetime_format` is not a valid format for the strftime method of the
            datetime.datetime class.
        """
        # Validate input plot parameters
        self._validate_plot_parameter_axes(axes)
        self._validate_plot_parameter_datetime_format(datetime_format)

        # Add secondary xaxis with the date_time
        axes2 = axes.twiny()
        axes2.set_xscale(axes.get_xscale())
        # Set major and minor ticks
        for minor in [False, True]:
            axes2.set_xticks(axes.get_xticks(minor=minor), minor=minor)
        # Set major and minor tick labels
        for minor in [False, True]:
            axes2.set_xticklabels(
                [
                    self.days_to_date_time(t).strftime(datetime_format)
                    for t in axes.get_xticks(minor=minor)
                ],
                rotation=45,
                ha="left",
                minor=minor,
            )
        # Set x-limits and label
        axes2.set_xlim(axes.get_xlim())
        axes2.set_xlabel("Date and Time")

        return axes

    @staticmethod
    def _validate_plot_parameter_axes(axes: Axes | None) -> None:
        """
        Private method to validate the 'axes' parameter of the plot methods.
        """
        if axes is not None and not isinstance(axes, Axes):
            raise TypeError(
                "Expected 'Axes' type or None for 'axes' parameter, but got {type(axes)}."
            )

    @staticmethod
    def _validate_plot_parameter_log_time(log_time: bool) -> None:
        """
        Private method to validate the 'log_time' parameter of the plot methods.
        """
        if not isinstance(log_time, bool):
            raise TypeError(
                f"Expected 'bool' type for 'log_time' parameter, but got {type(log_time)}."
            )

    @staticmethod
    def _validate_plot_parameter_min_log_time(min_log_time: float) -> None:
        """
        Private method to validate the 'min_log_time' parameter of the plot methods.
        """
        if not isinstance(min_log_time, (int, float)):
            raise TypeError(
                f"Expected 'float' type for 'min_log_time' parameter, but got {type(min_log_time)}."
            )

        if min_log_time <= 0.0:
            raise ValueError("The 'min_log_time' parameter must be greater than 0.0.")

    @staticmethod
    def _validate_plot_parameter_add_date_time(add_date_time: bool) -> None:
        """
        Private method to validate the 'add_date_time' parameter of the plot methods.
        """
        if not isinstance(add_date_time, bool):
            raise TypeError(
                f"Expected 'bool' type for 'add_date_time' parameter, but got {type(add_date_time)}."
            )

    @staticmethod
    def _validate_plot_parameter_datetime_format(datetime_format: str) -> None:
        """
        Private method to validate the 'datetime_format' parameter of the plot methods.
        """
        if not isinstance(datetime_format, str):
            raise TypeError(
                f"Expected 'str' type for 'datetime_format' parameter, but got {type(datetime_format)}."
            )

        try:
            datetime.datetime.now().strftime(datetime_format)
        except ValueError:
            raise ValueError(
                "The 'datetime_format' parameter is not a valid format for the strftime method "
                + "of the datetime.datetime class."
            )
