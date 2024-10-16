import datetime
import os

import matplotlib.pyplot as plt
from nuclei.client import NucleiClient

from baec.measurements.io.basetime import BaseTimeBucket, Credentials
from baec.measurements.measured_settlement_series import MeasuredSettlementSeries
from baec.model.fitcore import FitCoreModelGenerator

workdir = os.path.dirname(os.path.abspath(__file__))

client = NucleiClient()

# get AWS credentials
credentials = Credentials()

# create bucket manager
manage_project = BaseTimeBucket(credentials)

# get all the rod_id available to the user
projects_ids = manage_project.get_users_projects_ids()
for key, items in projects_ids.items():
    for item in items:
        try:
            # create settlement rod measurement series from BaseTime Bucket
            measurements = manage_project.make_settlement_rod_measurement_series(
                project=key, rod_id=item
            )

            # create figures
            fig = measurements.plot_xyz_time()
            fig.savefig(f"{workdir}/figs/{key}-{item}.png")
            plt.show(block=False)
            plt.pause(3)
            plt.close(fig)

            # Create series from measurements
            series = MeasuredSettlementSeries(
                measurements,
                start_date_time=measurements.measurements[0].date_time
                + datetime.timedelta(days=0),
            )

            # create figures
            fig = series.plot_displacements_time()
            fig.savefig(f"{workdir}/figs/{key}-{item}-displacements.png")
            plt.show(block=False)
            plt.pause(3)
            plt.close(fig)

            # generate fitcore model
            model = FitCoreModelGenerator(
                series=series,
                client=client,
            )
            fig = model.plot_fill_settlement_time(
                log_time=False,
                end_date_time=measurements.measurements[-1].date_time
                + datetime.timedelta(days=10),
            )
            fig.savefig(f"{workdir}/figs/{key}-{item}-settlement.png")
            plt.show(block=False)
            plt.pause(3)
            plt.close(fig)

        # catch error and print it to console.
        except ValueError as e:
            print(f"ERROR:{key}-{item};{e}")
