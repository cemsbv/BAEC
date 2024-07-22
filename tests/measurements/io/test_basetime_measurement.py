import pandas as pd

import sys
sys.path.insert(0,'D:/BAEC_CEMS/BAEC/src')

from baec.measurements.basetime_measurements import ProjectsIDs

'''
Test script for the Basetime connection.
Credentials file is not loaded in env, but stored locally

testing:
    -Output when calling company, projects, object IDs
    -Output when calling a series of an object ID
'''

with open('C:/Temp/test_class/cems_accessKeys.csv') as credfile:

    manage_project = ProjectsIDs(credfile)

print(manage_project.get_users_projects_ids())
test_series = manage_project.make_SettlementRodMeasurementSeries(company='Demo',project='Hansweert',rod_id='277-2')
print(test_series.to_dataframe())