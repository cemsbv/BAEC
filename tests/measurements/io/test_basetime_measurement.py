import pandas as pd

from baec.measurements.basetime_measurements import ProjectsIDs

"""
Test script for the Basetime connection.
Credentials file is not loaded in env, but stored locally

testing:
    -Output when calling company, projects, object IDs
    -Output when calling a series of an object ID
"""

with open("cems_accessKeys.csv") as credfile:
    manage_project = ProjectsIDs(credfile)

print(manage_project.get_users_projects_ids())
test_series = manage_project.make_SettlementRodMeasurementSeries(
    company="Van Oord", project="Voorbelasting Wilderszijde Lansingerland", rod_id="ZB1001"
)
print(test_series.to_dataframe())
