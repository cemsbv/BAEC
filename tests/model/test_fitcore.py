import datetime
import os

import matplotlib.pyplot as plt
import requests_mock
from nuclei.client import NucleiClient

from baec.measurements.io.zbase import measurements_from_zbase
from baec.measurements.measured_settlement_series import MeasuredSettlementSeries
from baec.model.fitcore import BASE_URL, FitCoreModelGenerator


def test_fitcore_model_generator() -> None:
    """Test fit and predict a series of measurements for a single settlement rod."""

    real_http = False
    show = False

    filepath = os.path.join(
        os.path.dirname(__file__), "../measurements/io/data/E990M.csv"
    )

    client = NucleiClient()

    # Create measurements from zbase csv file
    measurements = measurements_from_zbase(
        filepath_or_buffer=filepath, project_name="unitTest"
    )
    # Create series from measurements
    series = MeasuredSettlementSeries(
        measurements,
        start_date_time=measurements.measurements[0].date_time
        + datetime.timedelta(days=80),
    )

    # mock API calls
    if not real_http:
        with requests_mock.Mocker() as m:
            m.post(
                BASE_URL + f"simpleKoppejan/fit",
                json={
                    "popt": {
                        "primarySettlement": 47.43,
                        "shift": 0,
                        "hydrodynamicPeriod": 1.73,
                        "finalSettlement": 2.29,
                    }
                },
            )
            m.post(BASE_URL + f"simpleKoppejan/predict", json={"settlement": [0] * 500})

            # generate fitcore model
            model = FitCoreModelGenerator(
                series=series,
                client=client,
            )

            model.plot_fill_settlement_time(log_time=False)
    else:
        # generate fitcore model
        model = FitCoreModelGenerator(
            series=series,
            client=client,
        )

        model.plot_fill_settlement_time(log_time=False)

    # Show the plots
    if show:
        plt.show()

    plt.close("all")
