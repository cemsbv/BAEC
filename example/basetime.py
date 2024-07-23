import os

import matplotlib.pyplot as plt

from baec.measurements.io.basetime import BaseTimeBucket, Credentials

workdir = os.path.dirname(os.path.abspath(__file__))

# get AWS credentials
credentials = Credentials()

# create bucket manager
manage_project = BaseTimeBucket(credentials)

# get all the rod_id available to the user
projects_ids = manage_project.get_users_projects_ids()
for key, items in projects_ids["Demo"].items():
    for item in items:
        try:
            # create settlement rod measurement series
            series = manage_project.make_settlement_rod_measurement_series(
                company="Demo", project=key, rod_id=item
            )

            # create figures
            fig = series.plot_xyz_time()
            fig.savefig(f"{workdir}/figs/{key}-{item}.png")
            plt.show(block=False)
            plt.pause(3)
            plt.close(fig)
        # catch error and print it to console.
        except ValueError as e:
            print(f"ERROR:{key}-{item};{e}")
