import os

import matplotlib.pyplot as plt
from nuclei.client import NucleiClient

from baec.measurements.io.zbase import measurements_from_zbase
from baec.model.fitcore import FitCoreModelGenerator


def test_fitcore_model_generator() -> None:
    """Test fit and predict a series of measurements for a single settlement rod."""

    filepath = os.path.join(
        os.path.dirname(__file__), "../measurements/io/data/E990M.csv"
    )

    client = NucleiClient()

    # Create series from zbase csv file
    series = measurements_from_zbase(
        filepath_or_buffer=filepath, project_name="unitTest"
    )

    model = FitCoreModelGenerator(
        series=series,
        client=client,
        offset_start_settlement=80,
    )

    assert isinstance(model.plot(), plt.Axes)
