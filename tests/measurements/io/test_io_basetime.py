import os

import matplotlib.pyplot as plt
import pandas as pd

from baec.measurements.io.basetime import BaseTimeBucket, Credentials


def test_io_basetime() -> None:
    """
    Test script for the Basetime connection.
    Credentials file is not loaded in env, but stored locally

    testing:
        -Output when calling company, projects, object IDs
        -Output when calling a series of an object ID
    """
    show = False

    # get AWS credentials
    credentials = Credentials()

    manage_project = BaseTimeBucket(credentials)

    print(manage_project.get_users_projects_ids())
    series = manage_project.make_settlement_rod_measurement_series(
        company="Demo", project="Hansweert", rod_id="277-2"
    )
    assert isinstance(series.to_dataframe(), pd.DataFrame)

    series.plot_xyz_time()

    # Show the plots
    if show:
        plt.show()

    plt.close("all")
