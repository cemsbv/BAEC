import datetime
import os
from pathlib import Path

import matplotlib.pyplot as plt
import requests_mock
from nuclei.client import NucleiClient

from baec.measurements.io.zbase import measurements_from_zbase
from baec.measurements.measured_settlement_series import MeasuredSettlementSeries
from baec.model.fitcore import BASE_URL, FitCoreModelGenerator

dirpath = Path("example/website/")
if not dirpath.exists():
    dirpath.mkdir(parents=True)

# # Connect to the Measurements database
# database = BaseTimeBucket(
#     credentials=Credentials(),
#     s3bucket="my_bucket",
# )

# # Request data for a given company, project and rod_id
# measurement_series = database.make_settlement_rod_measurement_series(
#     company="my_company",
#     project="my_project",
#     rod_id="my_rod_id",
# )


# Create measurements from zbase csv file
rod_id = "E990M"
measurement_series = measurements_from_zbase(
    filepath_or_buffer=dirpath.joinpath("E990M.csv"), project_name="Example for website"
)

# Visualize the measurements
fig = measurement_series.plot_xyz_time()
# fig.set_size_inches(18.75, 7.5)
fig.set_size_inches(15, 10)
plt.savefig(dirpath.joinpath(f"measurements_{rod_id}.png"))


# Create settlement series from measurements
settlement_series = MeasuredSettlementSeries(
    series=measurement_series,
    start_date_time=datetime.datetime(2015, 1, 18),
)

# Visualize the settlements
fig = settlement_series.plot_fill_settlement_time()
fig.set_size_inches(15, 7.5)
plt.savefig(dirpath.joinpath(f"settlements_{rod_id}.png"))


# os.environ[
#     "NUCLEI_TOKEN"
# ] = ##

#  Fit a simple Koppejan model to the settlements
model = FitCoreModelGenerator(
    series=settlement_series,
    client=NucleiClient(),
)

fig = model.plot_fill_settlement_time()

fig.set_size_inches(15, 7.5)
plt.savefig(dirpath.joinpath(f"model_fit_{rod_id}.png"))

print(NucleiClient().user_permissions)