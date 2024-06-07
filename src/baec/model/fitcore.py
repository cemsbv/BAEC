from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
from dateutil.parser import isoparse
from matplotlib.pyplot import Axes
from nuclei.client import NucleiClient
from nuclei.client.utils import serialize_jsonifyable_object

from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)

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


@dataclass
class FitCoreResult:
    """Object containing the results of a predict call."""

    settlement: Sequence
    """Settlement [m]"""


class FitCoreModelGenerator:
    def __init__(
        self,
        series: SettlementRodMeasurementSeries,
        client: NucleiClient,
        offset_start_settlement: int = 0,
    ):
        """


        Parameters
        ----------
        series : SettlementRodMeasurementSeries
            Represents a series of measurements for a single settlement rod.
        client : NucleiClient
        offset_start_settlement : int
            TimeDelta of the start settlement based from start of measurements [days]
        """

        self._series = series
        self._client = client
        self._set_offset_start_settlement(offset_start_settlement)

    def _set_offset_start_settlement(self, value: int) -> None:
        """
        Private setter for project attribute.
        """
        if not isinstance(value, int):
            raise TypeError(
                "Expected 'int' type for 'offset_start_settlement' attribute."
            )
        if value < 0:
            raise ValueError(
                "Negative value not allowed for 'offset_start_settlement' attribute."
            )
        self._offset_start_settlement = value

    @property
    def offset_start_settlement(self) -> int:
        """TimeDelta of the start settlement based from start of measurements [days]"""
        return self._offset_start_settlement

    @offset_start_settlement.setter
    def offset_start_settlement(self, value: int) -> None:
        self._set_offset_start_settlement(value)

    @property
    def series(self) -> SettlementRodMeasurementSeries:
        """Represents a series of measurements for a single settlement rod."""
        return self._series

    def fit(self) -> FitCoreModel:
        """
        Fit the settlement measurements for a single settlement rod on
        a simplification of the Koppejan formula based on Arcadis
        Handleiding ZBASE en ZBASE analyse, versie 7.0; d.d. 31-10-2011

        Returns
        -------
        model : FitCoreModel
        """
        # TODO this will be done by the MeasuredFillAndSettlements class
        offset = self.series.to_dataframe()["plate_bottom_z"][0]

        payload = {
            "timeSeries": [
                isoparse(x.isoformat()) for x in self.series.to_dataframe()["date_time"]
            ],
            "settlementSeries": -(
                self.series.to_dataframe()["plate_bottom_z"].to_numpy(float) - offset
            ),
            "startDay": self.offset_start_settlement,
        }

        response = self._client.session.post(
            url=BASE_URL + f"simpleKoppejan/fit",
            json=serialize_jsonifyable_object(payload),
        )

        if not response.ok:
            raise RuntimeError(response.text)

        return FitCoreModel(**response.json()["popt"])

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

        payload = {"days": days} | self.fit().__dict__

        response = self._client.session.post(
            url=BASE_URL + f"simpleKoppejan/predict",
            json=serialize_jsonifyable_object(payload),
        )

        if not response.ok:
            raise RuntimeError(response.text)

        return FitCoreResult(**response.json())

    def plot(
        self,
        axes: Optional[Axes] = None,
        figsize: Tuple[float, float] = (8, 10),
        **kwargs: Any,
    ) -> Axes:
        """
        Plot the settlement prediction results on an `Axes' object.

        Parameters
        ----------
        axes:
            Optional `Axes` object where the settlement prediction can be plotted on.
            If not provided, a new `plt.Figure` will be activated and the `Axes`
            object will be created and returned.
        figsize:
            Size of the activate figure, as the `plt.figure()` argument.
        **kwargs:
            All additional keyword arguments are passed to the `pyplot.subplots()` call.

        Returns
        -------
        axes:
            The `Axes` object where the bearing capacities were plotted on.
        """

        # Create axes objects if not provided
        if axes is not None:
            if not isinstance(axes, Axes):
                raise ValueError(
                    "'axes' argument to plot() must be a `pyplot.axes.Axes` object or None."
                )
        else:
            kwargs_subplot = {
                "figsize": figsize,
                "tight_layout": True,
            }

            kwargs_subplot.update(kwargs)

            _, axes = plt.subplots(1, 1, **kwargs_subplot)

            if not isinstance(axes, Axes):
                raise ValueError(
                    "Could not create Axes objects. This is probably due to invalid matplotlib keyword arguments. "
                )

        # TODO add plot methode to series object
        offset = self.series.to_dataframe()["plate_bottom_z"][0]
        axes.plot(
            self.series.to_dataframe()["date_time"],
            (offset - self.series.to_dataframe()["plate_bottom_z"]) * -1,
            "-o",
            label="z;m",
        )
        offset = self.series.to_dataframe()["ground_surface_z"][0]
        axes.plot(
            self.series.to_dataframe()["date_time"],
            self.series.to_dataframe()["ground_surface_z"] - offset,
            "-o",
            label="ground_surface_z",
        )

        # add settlement prediction subplot
        days = np.arange(0, 500, step=1, dtype=int)
        x = [
            self.series.to_dataframe()["date_time"][0]
            + timedelta(self.offset_start_settlement)
            + timedelta(int(day))
            for day in days
        ]
        axes.plot(
            x,
            np.array(self.predict(days).settlement) * -1,
            label="z;p",
        )

        return axes
