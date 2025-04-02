from __future__ import annotations

import datetime
import logging
import re
from ast import Dict, Str
from copy import deepcopy
from dataclasses import dataclass
from typing import Literal, Sequence, Tuple

import numpy as np
from dateutil.parser import isoparse
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter
from nuclei.client import NucleiClient
from nuclei.client.utils import serialize_jsonifyable_object

from baec.measurements import plot_utils
from baec.measurements.measured_settlement_series import MeasuredSettlementSeries

BASE_URL = "https://crux-nuclei.com/api/settlecore/v1/"


@dataclass
class FitCoreModel:
    """Object containing the results of a fit call."""

    primarySettlement: float
    """Primary settlement [%]"""
    shift: float
    """Shift [days]"""
    hydrodynamicPeriod: float
    """Hydrodynamic period [year]"""
    finalSettlement: float
    """Final settlement [m]"""
    client: NucleiClient | None = None
    """Nuclei client, required to make predictions (optional). Default is None."""
    measured_settlements: MeasuredSettlementSeries | None = None
    """The measurements used to fit the model (optional). Default is None."""

    @classmethod
    def default(cls) -> FitCoreModel:
        return cls(
            primarySettlement=0.0,
            shift=0.0,
            hydrodynamicPeriod=0.0,
            finalSettlement=0.0,
        )

    def predict(self, days: Sequence[int]) -> FitCoreResult2:
        """
        Predict the settlement for any day with on a simplification of
        the Koppejan formula based on Arcadis Handleiding ZBASE en
        ZBASE analyse, versie 7.0; d.d. 31-10-2011


        Parameters
        ----------
        days : Sequence[int]
            TimeDelta of the start settlement based from start of measurements [days]

        Returns
        -------
        result : FitCoreResult
        """

        assert isinstance(
            self.client, NucleiClient
        ), "Client is not set. It is required to make predictions."

        params = deepcopy(self.__dict__)
        params.pop("client")

        payload = {"days": days} | params

        response = self.client.session.post(
            url=BASE_URL + "simpleKoppejan/predict",
            json=serialize_jsonifyable_object(payload),
        )

        if not response.ok:
            raise RuntimeError(response.text)

        kwargs = response.json() | {"days": days}

        return FitCoreResult2(**kwargs)


@dataclass
class FittedFitCoreModel:
    model: FitCoreModel
    """The fitted FitCore model."""
    measured_settlements: MeasuredSettlementSeries
    """The measurements used to fit the model."""
    predicted_settlements: FitCoreResult2 | None = None
    """The predicted settlements based on the fitted model."""

    def predict(
        self,
        start_days_or_datetime: float | datetime.datetime = 0.0,
        end_days_or_datetime: float | datetime.datetime = 11000.0,
        step: float = 1.0,
    ) -> None:
        if isinstance(start_days_or_datetime, datetime.datetime):
            if start_days_or_datetime < self.measured_settlements.start_date_time:
                raise ValueError("Start datetime cannot be before start datetime.")
            start_time_delta = (
                start_days_or_datetime - self.measured_settlements.start_date_time
            )
        elif isinstance(start_days_or_datetime, float):
            start_time_delta = datetime.timedelta(days=start_days_or_datetime)
        else:
            raise TypeError(
                f"Attribute `start_days_or_datetime` must be `None` or of type `float` or `datetime`, but got {type(start_days_or_datetime)}"
            )

        if isinstance(end_days_or_datetime, datetime.datetime):
            if end_days_or_datetime < self.measured_settlements.start_date_time:
                raise ValueError("End datetime cannot be before start datetime.")
            end_time_delta = (
                end_days_or_datetime - self.measured_settlements.start_date_time
            )
        elif isinstance(end_days_or_datetime, float):
            end_time_delta = datetime.timedelta(days=end_days_or_datetime)
        else:
            raise TypeError(
                f"Attribute `end_days_or_datetime` must be of type `float` or `datetime`, but got {type(end_days_or_datetime)}"
            )

        self.predicted_settlements = self.model.predict(
            days=np.arange(
                start_time_delta.days, end_time_delta.days, step=step, dtype=float
            )
        )

    def plot_predicted_settlement_time(
        self,
        axes: Axes | None = None,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
        invert_yaxis: bool = True,
        add_model_parameters: bool = True,
    ) -> Axes:
        """
        Plot the settlement of the initial ground profile rod over time.

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
        end_date_time: datetime.datetime | int, optional
            End date time of the predicted settlement, Can be datetime object or integer. If integer number
            corresponds to the number of days from `start_date_time` of the MeasuredSettlementSeries.
            Default is 100
        invert_yaxis: bool, optional
            Whether the yaxis is oriented in the "inverse" direction.
            Default is True
        add_model_parameters: bool, optional
            Whether the model parameters are added to the plot
            Default is True

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

        assert isinstance(
            self.predicted_settlements, FitCoreResult2
        ), "Predicted settlements are not available. Call `predict` method first."

        # Validate input plot parameters
        plot_utils.validate_plot_parameter_axes(axes)
        plot_utils.validate_plot_parameter_log_time(log_time)
        plot_utils.validate_plot_parameter_min_log_time(min_log_time)
        plot_utils.validate_plot_parameter_add_date_time(add_date_time)
        plot_utils.validate_plot_parameter_datetime_format(datetime_format)

        # If axes is None create new Axes.
        if axes is None:
            plt.figure()
            axes = plt.gca()

        # Plot the property data over time
        days = self.predicted_settlements.days
        settlement = self.predicted_settlements.settlement
        axes.plot(days, settlement)

        if log_time:
            axes.set_xlim(min_log_time, max(days) + 1.0)
            axes.set_xscale("log")

        axes.set_ylim(min(settlement) - 0.5, max(settlement) + 0.5)
        if invert_yaxis:
            axes.invert_yaxis()

        axes.xaxis.set_major_formatter(ScalarFormatter())
        axes.xaxis.set_minor_formatter(ScalarFormatter())
        axes.grid(visible=True, which="both")

        axes.set_ylabel(
            f"Settlement [{self.measured_settlements.coordinate_reference_systems.vertical_units}]"
        )
        axes.set_xlabel("Time [days]")
        axes.set_title(
            f"Predicted settlement of initial ground surface for object: {self.measured_settlements.object_id}"
        )

        # Add secondary xaxis with the date_time
        if add_date_time:
            axes = self.measured_settlements._add_datetime_as_secondary_axis(
                axes=axes, datetime_format=datetime_format
            )

        # Add text to the Axes.
        # if add_model_parameters:
        #     label = """FitCore model parameters:
        #         \n final settlement = {:.2f}
        #         \n hydrodynamic period = {:.2f}
        #         \n shift = {:.2f}
        #         \n primary settlement = {:.2f}""".format(
        #         self.model.finalSettlement,
        #         self.model.hydrodynamicPeriod,
        #         self.model.shift,
        #         self.model.primarySettlement,
        #     )
        #     axes.text(
        #         # np.mean(days),
        #         days[0],
        #         # 0,
        #         np.max(self.predicted_settlements.settlement),
        #         label,
        #         style="italic",
        #         bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 10},
        #         fontsize=2,
        #         horizontalalignment="center",
        #         verticalalignment="center",
        #     )

        return axes

    def plot_fill_settlement_time(
        self,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
        fig: Figure | None = None,
        axes: Tuple[Axes, Axes] | None = None,
    ) -> Figure:
        """
        Plot in a new fill thickness and the settlement of the initial ground profile
        relative to the zero measurement over time.

        Parameters
        ----------
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
        end_date_time: datetime.datetime | int, optional
            End date time of the predicted settlement, Can be datetime object or integer. If integer number
            corresponds to the number of days from `start_date_time` of the MeasuredSettlementSeries.
            Default is 100

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
        if fig is None:
            fig, axes = plt.subplots(2, 1, figsize=(10, 20), sharex=True)

        self.measured_settlements.plot_fill_time(
            axes=axes[0],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=add_date_time,
            datetime_format=datetime_format,
        )
        axes[0].set_title("")
        axes[0].set_xlabel("")

        # add settlement prediction secondary axes
        self.measured_settlements.plot_settlement_time(
            axes=axes[1],
            log_time=False,
            min_log_time=min_log_time,
            add_date_time=False,
            datetime_format=datetime_format,
        )

        self.plot_predicted_settlement_time(
            axes=axes[1],
            log_time=log_time,  # TODO: fix min and max boundaries
            min_log_time=min_log_time,
            add_date_time=False,
            datetime_format=datetime_format,
            invert_yaxis=True,
            add_model_parameters=True,
        )

        axes[1].set_title("")
        axes[1].legend(["measured", "fitted_model"])

        if add_date_time:
            fig.subplots_adjust(top=0.825, hspace=0.075)

        # fig.suptitle(
        #     f"Fill thickness and settlement for object: {self.measured_settlements.object_id}"
        # )

        return fig


@dataclass
class FitCoreResult:
    """Object containing the results of a predict call."""

    settlement: Sequence
    """Settlement [m]"""


@dataclass
class FitCoreResult2:
    """Object containing the results of a predict call."""

    days: Sequence[float]
    """Time [days]"""
    settlement: Sequence[float]
    """Settlement [m]"""


@dataclass
class ParameterSetting:
    pass


@dataclass
class FreeParameterBounds:
    lower_bound: float | None = None
    upper_bound: float | None = None

    def to_dict(self) -> Dict[Literal["upperBound", "lowerBound"], float | None] | None:
        if self.lower_bound is None and self.upper_bound is None:
            return None
        return {"upperBound": self.upper_bound, "lowerBound": self.lower_bound}


@dataclass
class FixedParameter:
    pass


@dataclass
class FittingParameters:
    primarySettlement: FixedParameter | FreeParameterBounds
    shift: FixedParameter | FreeParameterBounds
    hydrodynamicPeriod: FixedParameter | FreeParameterBounds
    finalSettlement: FixedParameter | FreeParameterBounds

    @classmethod
    def all_free(cls) -> FittingParameters:
        return cls(
            primarySettlement=FreeParameterBounds(),
            shift=FreeParameterBounds(),
            hydrodynamicPeriod=FreeParameterBounds(),
            finalSettlement=FreeParameterBounds(),
        )

    @classmethod
    def all_fixed(cls) -> FittingParameters:
        return cls(
            primarySettlement=FixedParameter(),
            shift=FixedParameter(),
            hydrodynamicPeriod=FixedParameter(),
            finalSettlement=FixedParameter(),
        )

    @classmethod
    def all_fixed_except(
        cls,
        free_parameters: Sequence[
            Literal[
                "primarySettlement",
                "shift",
                "hydrodynamicPeriod",
                "finalSettlement",
            ]
            | Tuple[
                Literal[
                    "primarySettlement",
                    "shift",
                    "hydrodynamicPeriod",
                    "finalSettlement",
                ],
                FreeParameterBounds,
            ]
        ],
    ) -> FittingParameters:
        fitting_parameters = cls.all_fixed()

        for free_parameter in free_parameters:
            parameter_name = free_parameter[0]

            # Get the free parameter bounds (use default if not provided)
            if isinstance(free_parameter, str):
                free_parameter_bounds = FreeParameterBounds()
            else:
                free_parameter_bounds = free_parameter[1]

            setattr(fitting_parameters, parameter_name, free_parameter_bounds)

        return fitting_parameters

    @classmethod
    def all_free_except(
        cls,
        fixed_parameters: Sequence[
            Literal[
                "primarySettlement", "shift", "hydrodynamicPeriod", "finalSettlement"
            ]
        ],
    ) -> FittingParameters:
        fitting_parameters = cls.all_free()

        for parameter_name in fixed_parameters:
            setattr(fitting_parameters, parameter_name, FixedParameter())

        return fitting_parameters


class FitCoreModelGenerator2:
    def __init__(
        self,
        base_model: FitCoreModel,
        fitting_parameters: FittingParameters,
        client: NucleiClient,
    ):
        """


        Parameters
        ----------
        series : MeasuredSettlementSeries
            Represents a series of measurements for a single settlement rod.
        client : NucleiClient
        """
        self._base_model = base_model
        self._fitting_parameters = fitting_parameters
        self._client = client

    def fit(
        self, measured_settlement_series: MeasuredSettlementSeries
    ) -> FittedFitCoreModel:
        """
        Fit the settlement measurements for a single settlement rod on
        a simplification of the Koppejan formula based on Arcadis
        Handleiding ZBASE en ZBASE analyse, versie 7.0; d.d. 31-10-2011

        Returns
        -------
        model : FitCoreModel
        """

        # create payload for the fit API call
        payload = {
            "timeSeries": [
                isoparse(x.isoformat())
                for x in measured_settlement_series.to_dataframe()["date_time"]
            ],
            "settlementSeries": measured_settlement_series.settlements,
            "startDay": 0,
            "settings": self._settings_payload,
        }

        # print("fit payload", payload)

        # call endpoint
        response = self._client.session.post(
            url=BASE_URL + "simpleKoppejan/fit",
            json=serialize_jsonifyable_object(payload),
        )

        if not response.ok:
            raise RuntimeError(response.text)

        # add client
        kwargs = response.json()["popt"] | {"client": self._client}

        return FittedFitCoreModel(
            model=FitCoreModel(**kwargs),
            measured_settlements=measured_settlement_series,
        )

    @property
    def _settings_payload(
        self,
    ) -> Dict[
        Literal["primarySettlement", "shift", "hydrodynamicPeriod", "finalSettlement"],
        Dict[Literal["upperBound", "LowerBound"], float],
    ]:
        settings = {}
        for parameter in [
            "primarySettlement",
            "shift",
            "hydrodynamicPeriod",
            "finalSettlement",
        ]:
            fitting_setting = getattr(self._fitting_parameters, parameter)

            if isinstance(fitting_setting, FixedParameter):
                fixed_value = getattr(self._base_model, parameter)
                settings.update(
                    {
                        f"{parameter}": {
                            "upperBound": fixed_value,
                            "lowerBound": fixed_value - 1e-8,
                        }
                    }
                )
            # Else the fitting setting is FreeParameterBounds
            else:
                bounds_dict = getattr(self._fitting_parameters, parameter).to_dict()
                if bounds_dict is not None:
                    settings.update({f"{parameter}": bounds_dict})

        return settings

        # return {
        #     "primarySettlement": {
        #         "upperBound": self._base_model.primarySettlement
        #         if isinstance(
        #             self._fitting_parameters.primarySettlement, FixedParameter
        #         )
        #         else self._fitting_parameters.primarySettlement.upper_bound,
        #         "lowerBound": self._base_model.primarySettlement
        #         if isinstance(
        #             self._fitting_parameters.primarySettlement, FixedParameter
        #         )
        #         else self._fitting_parameters.primarySettlement.lower_bound,
        #     },
        #     "shift": {
        #         "upperBound": self._base_model.shift
        #         if isinstance(self._fitting_parameters.shift, FixedParameter)
        #         else self._fitting_parameters.shift.upper_bound,
        #         "lowerBound": self._base_model.shift
        #         if isinstance(self._fitting_parameters.shift, FixedParameter)
        #         else self._fitting_parameters.shift.lower_bound,
        #     },
        #     "hydrodynamicPeriod": {
        #         "upperBound": self._base_model.hydrodynamicPeriod
        #         if isinstance(
        #             self._fitting_parameters.hydrodynamicPeriod, FixedParameter
        #         )
        #         else self._fitting_parameters.hydrodynamicPeriod.upper_bound,
        #         "lowerBound": self._base_model.hydrodynamicPeriod
        #         if isinstance(
        #             self._fitting_parameters.hydrodynamicPeriod, FixedParameter
        #         )
        #         else self._fitting_parameters.hydrodynamicPeriod.lower_bound,
        #     },
        #     "finalSettlement": {
        #         "upperBound": self._base_model.finalSettlement
        #         if isinstance(self._fitting_parameters.finalSettlement, FixedParameter)
        #         else self._fitting_parameters.finalSettlement.upper_bound,
        #         "lowerBound": self._base_model.finalSettlement
        #         if isinstance(self._fitting_parameters.finalSettlement, FixedParameter)
        #         else self._fitting_parameters.finalSettlement.lower_bound,
        #     },
        # }


# def to_snake_case(name):
#     name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
#     name = re.sub('__([A-Z])', r'_\1', name)
#     name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
#     return name.lower()


# def camel_to_snake(name):
#     name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
#     return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class FitCoreModelGenerator:
    def __init__(
        self,
        series: MeasuredSettlementSeries,
        client: NucleiClient,
    ):
        """


        Parameters
        ----------
        series : MeasuredSettlementSeries
            Represents a series of measurements for a single settlement rod.
        client : NucleiClient
        """

        self._series = series
        self._client = client
        self._hash_settlements_ = deepcopy(tuple(self.series.settlements).__hash__())
        self._model = self.fit(force=True)

    @property
    def series(self) -> MeasuredSettlementSeries:
        """Represents a series of measurements for a single settlement rod."""
        return self._series

    def fit(self, force: bool = True) -> FitCoreModel:
        """
        Fit the settlement measurements for a single settlement rod on
        a simplification of the Koppejan formula based on Arcadis
        Handleiding ZBASE en ZBASE analyse, versie 7.0; d.d. 31-10-2011

        Returns
        -------
        model : FitCoreModel
        """

        # check if the __hash__ of the MeasuredSettlementSeries has changed
        # if not no need to refit the series
        if (
            not force
            and self._hash_settlements_ == tuple(self.series.settlements).__hash__()
        ):
            logging.info("Series has not changed. Use cached FitCoreModel")
            return self._model

        # create payload for the fit API call
        payload = {
            "timeSeries": [
                isoparse(x.isoformat()) for x in self.series.to_dataframe()["date_time"]
            ],
            "settlementSeries": self.series.settlements,
            "startDay": 0,
        }

        # call endpoint
        response = self._client.session.post(
            url=BASE_URL + "simpleKoppejan/fit",
            json=serialize_jsonifyable_object(payload),
        )

        if not response.ok:
            raise RuntimeError(response.text)

        # update cache properties
        self._hash_settlements_ = deepcopy(tuple(self.series.settlements).__hash__())
        self._model = FitCoreModel(**response.json()["popt"])

        return self._model

    def predict(self, days: Sequence[int]) -> FitCoreResult:
        """
        Predict the settlement for any day with on a simplification of
        the Koppejan formula based on Arcadis Handleiding ZBASE en
        ZBASE analyse, versie 7.0; d.d. 31-10-2011


        Parameters
        ----------
        days : Sequence[int]
            TimeDelta of the start settlement based from start of measurements [days]

        Returns
        -------
        result : FitCoreResult
        """

        payload = {"days": days} | self.fit(force=False).__dict__

        response = self._client.session.post(
            url=BASE_URL + "simpleKoppejan/predict",
            json=serialize_jsonifyable_object(payload),
        )

        if not response.ok:
            raise RuntimeError(response.text)

        return FitCoreResult(**response.json())

    def plot_settlement_time(
        self,
        axes: Axes | None = None,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
        end_date_time: datetime.datetime | int = 500,
        invert_yaxis: bool = True,
        add_model_parameters: bool = True,
    ) -> Axes:
        """
        Plot the settlement of the initial ground profile rod over time.

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
        end_date_time: datetime.datetime | int, optional
            End date time of the predicted settlement, Can be datetime object or integer. If integer number
            corresponds to the number of days from `start_date_time` of the MeasuredSettlementSeries.
            Default is 100
        invert_yaxis: bool, optional
            Whether the yaxis is oriented in the "inverse" direction.
            Default is True
        add_model_parameters: bool, optional
            Whether the model parameters are added to the plot
            Default is True

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

        # Validate input plot parameters
        plot_utils.validate_plot_parameter_axes(axes)
        plot_utils.validate_plot_parameter_log_time(log_time)
        plot_utils.validate_plot_parameter_min_log_time(min_log_time)
        plot_utils.validate_plot_parameter_add_date_time(add_date_time)
        plot_utils.validate_plot_parameter_datetime_format(datetime_format)

        # calculate the end date for the prediction
        if isinstance(end_date_time, datetime.datetime):
            if end_date_time < self.series.start_date_time:
                raise ValueError("End datetime cannot be before start datetime.")
            end_time_delta = end_date_time - self.series.start_date_time
        elif isinstance(end_date_time, int):
            end_time_delta = datetime.timedelta(days=end_date_time)
        else:
            raise ValueError(
                f"Attribute `end_time_delta` must be a datetime object or an int got a {type(end_date_time)}"
            )

        # If axes is None create new Axes.
        if axes is None:
            plt.figure()
            axes = plt.gca()

        # Plot the property data over time
        days = np.arange(0, end_time_delta.days, step=1, dtype=float)
        settlement = self.predict(days).settlement
        axes.plot(days, settlement)

        if log_time:
            axes.set_xlim(min_log_time, max(days) + 1.0)
            axes.set_xscale("log")

        axes.set_ylim(min(settlement) - 0.5, max(settlement) + 0.5)
        if invert_yaxis:
            axes.invert_yaxis()

        axes.xaxis.set_major_formatter(ScalarFormatter())
        axes.xaxis.set_minor_formatter(ScalarFormatter())
        axes.grid(visible=True, which="both")

        axes.set_ylabel(
            f"Settlement [{self.series.coordinate_reference_systems.vertical_units}]"
        )
        axes.set_xlabel("Time [days]")
        axes.set_title(
            f"Predicted settlement of initial ground surface for object: {self.series.object_id}"
        )

        # Add secondary xaxis with the date_time
        if add_date_time:
            axes = self.series._add_datetime_as_secondary_axis(
                axes=axes, datetime_format=datetime_format
            )

        # Add text to the Axes.
        if add_model_parameters:
            model = self.fit(force=False)
            label = """FitCore model parameters:
                \n final settlement = {:.2f}
                \n hydrodynamic period = {:.2f}
                \n shift = {:.2f}
                \n primary settlement = {:.2f}""".format(
                model.finalSettlement,
                model.hydrodynamicPeriod,
                model.shift,
                model.primarySettlement,
            )
            axes.text(
                np.mean(days),
                0,
                label,
                style="italic",
                bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 10},
                horizontalalignment="center",
                verticalalignment="center",
            )

        return axes

    def plot_fill_settlement_time(
        self,
        log_time: bool = True,
        min_log_time: float = 1.0,
        add_date_time: bool = True,
        datetime_format: str = "%d-%m-%Y",
        end_date_time: datetime.datetime | int = 500,
    ) -> Figure:
        """
        Plot in a new fill thickness and the settlement of the initial ground profile
        relative to the zero measurement over time.

        Parameters
        ----------
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
        end_date_time: datetime.datetime | int, optional
            End date time of the predicted settlement, Can be datetime object or integer. If integer number
            corresponds to the number of days from `start_date_time` of the MeasuredSettlementSeries.
            Default is 100

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
        fig, axes = plt.subplots(2, 1, figsize=(10, 20), sharex=True)

        self.series.plot_fill_time(
            axes=axes[0],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=add_date_time,
            datetime_format=datetime_format,
        )
        axes[0].set_title("")
        axes[0].set_xlabel("")

        # add settlement prediction secondary axes
        self.series.plot_settlement_time(
            axes=axes[1],
            log_time=log_time,
            min_log_time=min_log_time,
            add_date_time=False,
            datetime_format=datetime_format,
        )

        self.plot_settlement_time(
            axes=axes[1],
            log_time=False,
            min_log_time=min_log_time,
            add_date_time=False,
            datetime_format=datetime_format,
            end_date_time=end_date_time,
            invert_yaxis=True,
            add_model_parameters=True,
        )

        axes[1].set_title("")
        axes[1].legend(["measured", "fitted_model"])

        if add_date_time:
            fig.subplots_adjust(top=0.825, hspace=0.075)

        fig.suptitle(
            f"Fill thickness and settlement for object: {self.series.object_id}"
        )

        return fig
