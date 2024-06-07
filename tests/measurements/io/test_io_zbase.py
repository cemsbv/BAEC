import os

import pandas as pd

from baec.measurements.io.zbase import measurements_from_zbase


def test_io_zbase() -> None:
    """Test parsing zBase csv into SettlementRodMeasurementSeries object."""

    filepath = os.path.join(os.path.dirname(__file__), "data/E990M.csv")

    # Create series from zbase csv file
    series = measurements_from_zbase(
        filepath_or_buffer=filepath, project_name="unitTest"
    )

    assert isinstance(series.to_dataframe(), pd.DataFrame)
