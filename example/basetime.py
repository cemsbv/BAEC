import datetime
import os
from pathlib import Path

import matplotlib.pyplot as plt

from baec.measurements.io.basetime import BaseTimeBucket, Credentials
from baec.measurements.measured_settlement_series import MeasuredSettlementSeries

workdir = os.path.dirname(os.path.abspath(__file__))

# get AWS credentials
credentials = Credentials()

# create bucket manager
manage_project = BaseTimeBucket(credentials)


# get all the rod_id available to the user
projects_ids = manage_project.get_users_projects_ids()
for project, rod_ids in projects_ids["Demo"].items():
    # Create dirpath to store the figures for this project
    dirpath = Path(f"example/figs/{project}")
    if not dirpath.exists():
        dirpath.mkdir(parents=True)

    for rod_id in rod_ids:
        try:
            # create settlement rod measurement series
            measurement_series = manage_project.make_settlement_rod_measurement_series(
                company="Demo", project=project, rod_id=rod_id
            )

            # Visualize the measurements
            fig = measurement_series.plot_xyz_time()
            # fig.set_size_inches(18.75, 7.5)
            fig.set_size_inches(15, 10)
            plt.savefig(dirpath.joinpath(f"measurements_{rod_id}.png"))
            plt.close()

            # Create settlement series from measurements
            settlement_series = MeasuredSettlementSeries(
                series=measurement_series,
                # start_date_time=datetime.datetime(2015, 1, 18),
            )

            # Visualize the settlements
            fig = settlement_series.plot_fill_settlement_time()
            fig.set_size_inches(15, 7.5)
            plt.savefig(dirpath.joinpath(f"settlements_{rod_id}.png"))
            plt.close()

        # catch error and print it to console.
        except ValueError as e:
            print(f"ERROR:{project}-{rod_id};{e}")
