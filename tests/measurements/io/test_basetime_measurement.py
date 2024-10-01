import pandas as pd
from datetime import datetime

from baec.measurements.basetime_measurements import ProjectsIDs

"""
Test script for the Basetime connection.
Credentials file is not loaded in env, but stored locally

testing:
    -Output when calling company, projects, object IDs
    -Output when calling a series of an object ID
"""
print(datetime.now())
time_start = datetime.now()
with open("cems_accessKeys.csv") as credfile:
    manage_project = ProjectsIDs(credfile)
print(datetime.now()-time_start)
time_start = datetime.now()
print(manage_project.get_users_projects_ids())
test_series = manage_project.make_SettlementRodMeasurementSeries(
    project="Voorbelasting Wilderszijde Lansingerland", rod_id="ZB-1001"
)

print(test_series.to_dataframe())
print(datetime.now()-time_start)
time_start = datetime.now()
test_series = manage_project.make_SettlementRodMeasurementSeries(
    project="Voorbelasting Wilderszijde Lansingerland", rod_id="ZB-1001"
)
print(test_series.to_dataframe())
print(datetime.now()-time_start)
time_start = datetime.now()