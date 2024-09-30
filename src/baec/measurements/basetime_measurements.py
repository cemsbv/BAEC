from __future__ import annotations

import json
import re
from datetime import datetime
from os import PathLike
from typing import Dict, List

import boto3
import botocore
import pandas as pd
import pyproj
from pandas._typing import ReadCsvBuffer

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    StatusMessage,
    StatusMessageLevel,
)
from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)
from baec.project import Project


class ProjectsIDs:
    """
    Class object to get a list of projects and Point IDs or to import measurements as a SettlementRodMeasurementSeries.
    """

    def __init__(
        self,
        credentials: str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str]):
        """
        Initializes a ProjectsIDs object.

        Parameters
        ----------
        credentials : str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str]
            Any valid string path is acceptable. Credentials needs to refer to the AWS credential file given by Basetime.

        Returns
        -------
        series : ProjectsIDs [dict]
            A overview of all the available projects and connected settlement rods within every project. [dict]
            <Keys> : project names
            <Values> : list of Point IDs inside every project.

        series : SettlementRodMeasurementSeries
            A SettlementRodMeasurementSeries object for every available rod measurement, to be called within the class

        Raises
        ------
        ValueError/ClientError
            If the provided credential file does not contain the correct credentials.
            If the wrong type of value is given for the credential file.
        TypeError
            If the input types are incorrect.
            If the credential file does not contain credentials.
        ValueError
            If the list of measurements is empty.
            If the measurements are not for the same project, device or object.
        IOError
            If ZBASE file cannot be parsed by Pandas
        FileNotFoundError
            If filepath_or_buffer is requested but doesn't exist.
        """

        dic_user_projects_points = {}

        # Read the credentials file
        try:
            dict_credentials = pd.read_csv(credentials).to_dict("records")[0]
        except pd.errors.ParserError as e:
            raise IOError(
                f"Errors encountered while parsing contents of the credentials file: \n {e}"
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(e)
        except ValueError:
            raise ValueError(
                "Wrong type of credentials file given, str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str], Any valid string path is acceptable."
            )

        # Create boto3 client and resource for connecting to AWS S3
        s3c = boto3.client(
            service_name="s3",
            region_name="eu-west-1",
            aws_access_key_id=dict_credentials["Access key ID"],
            aws_secret_access_key=dict_credentials["Secret access key"],
        )
        s3r = boto3.resource(
            service_name="s3",
            region_name="eu-west-1",
            aws_access_key_id=dict_credentials["Access key ID"],
            aws_secret_access_key=dict_credentials["Secret access key"],
        )

        # Create boto3 client for using the lamdba functions
        lambda_client = boto3.client(
            service_name='lambda',
            region_name='eu-west-1',
            aws_access_key_id=dict_credentials["Access key ID"],
            aws_secret_access_key=dict_credentials["Secret access key"]
            )

        # Create the dictionary to translate the error codes. Get the error_codes file from the AWS S3 bucket
        dict_errors = {}
        try:
            for line in (
                s3r.Object('basetime-general', "error_codes.txt")
                .get()["Body"]
                .read()
                .decode("utf-8")
                .split("\n")
            ):
                error_line = line.split(",")
                dict_errors[int(error_line[0])] = {
                    "basetime error": error_line[1],
                    "description": error_line[2],
                    "status message level": error_line[3],
                }
        except botocore.exceptions.ClientError:
            raise ValueError(
                "The AWS Access Key ID you provided does not exist in our records."
            )

        # Initialize all attributes
        self.s3c = s3c
        self.s3r = s3r
        self.lambda_c = lambda_client
        self.credentials = dict_credentials["Access key ID"] + ',' + dict_credentials["Secret access key"]
        self.dict_errors = dict_errors
        self.dic_projects = self.get_users_projects_ids()

    def get_users_projects_ids(self) -> dict:
        """
        Call Lambda function in the Basetime AWS environment, to get the projets and point ID's of the objects the
        user is allow to get.
        Return the dictionary containing every User as a key, then the Project as key, the value is a list of all the Point IDs.
        - Company/user
            - projects
                - point IDs
        """

        function_name = 'api-gateway-project_get'
        payload = {
            "headers" : {"Authorization" : self.credentials},
        }

        response = self.lambda_c.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        response_ids = json.loads(response['Payload'].read())
        self.dic_projects = json.loads(response_ids['body'])
        return self.dic_projects

    def make_SettlementRodMeasurementSeries(
        self, project: str, rod_id: str
    ) -> SettlementRodMeasurementSeries:
        """
        Make a SettlementRodMeasurementSeries:

        Initialize by checking if the values are inside the S3 environment of Basetime, by using variable [dic_projects].
        Iterate through all the folders in the S3 environment. The environment has the following folder structure:
        - Company uuid
            - Folders with project uuids
                - Files of point uuids
                    - Each file contans a full history of all the measurements of the point uuid.
                    - Everytime a customers generates a new point uuid, a new file will be created.

        SettlementRodMeasurement creating:
            - Split Basetime EPSG code to list of EPSG numbers to add to CoordinateReferenceSystems
            - Split error codes into multiple StatusMessage classes
            - Add all values to the SettlementRodMeasurement class
        """
        if (
            project in self.dic_projects
            and rod_id in self.dic_projects[project]
        ):
            list_SettlementRodMeasurement = []

            function_name = 'api-gateway-get-data'

            payload = {
                "headers" : {
                    "Authorization" : self.credentials,
                    "Project" : project,
                    "Point_ID" : rod_id
                    },
            }

            response = self.lambda_c.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            response_payload = json.loads(response['Payload'].read())

            try:
                measurement_serie = json.loads(response_payload['body'])
            except KeyError:
                raise KeyError(
                    "Credentials missing for this Rod ID. Contact Basetime to grant access to the project."
                )

            list_epsg_codes=self.convert_epsg_string_to_list_int(measurement_serie['Coordinate projection'])
            if len(list_epsg_codes)==2:
                coordinate_reference_systems = CoordinateReferenceSystems(
                    pyproj.CRS.from_user_input(list_epsg_codes[0]),
                    pyproj.CRS.from_user_input(list_epsg_codes[1])
                    )
            elif len(list_epsg_codes)==1:
                coordinate_reference_systems = CoordinateReferenceSystems(
                    pyproj.CRS.from_user_input(list_epsg_codes[0]),
                    pyproj.CRS.from_user_input(list_epsg_codes[0])
                    )
            else:
                coordinate_reference_systems = CoordinateReferenceSystems(None)

            baec_project = Project(
                id_=measurement_serie["Project uuid"],
                name=measurement_serie["Project name"],
                )
            object_id = measurement_serie["Object ID"]

            for date_measurement in measurement_serie['Measurements']:

                measurement = measurement_serie['Measurements'][date_measurement]

                if measurement["Error Codes"] == " ":
                    status_messages = [
                        StatusMessage(
                            code=7000,
                            description="Measurement approved",
                            level=StatusMessageLevel.OK,
                        )
                    ]
                else:
                    status_messages = []
                    error_string_list = measurement["Error Codes"][1:-1].split(",")
                    error_integer_list = [int(num) for num in error_string_list]
                    for error_code in error_integer_list:
                        if (self.dict_errors[error_code]["status message level"] == "INFO"):
                            status_messages.append(
                                StatusMessage(
                                    code=error_code,
                                    description=self.dict_errors[error_code]["description"],
                                    level=StatusMessageLevel.INFO,
                                )
                            )
                        elif (
                            self.dict_errors[error_code]["status message level"] == "WARNING"):
                            status_messages.append(
                                StatusMessage(
                                    code=error_code,
                                    description=self.dict_errors[error_code]["description"],
                                    level=StatusMessageLevel.WARNING,
                                )
                            )
                        elif (
                            self.dict_errors[error_code]["status message level"] == "ERROR"):
                            status_messages.append(
                                StatusMessage(
                                    code=error_code,
                                    description=self.dict_errors[error_code]["description"],
                                    level=StatusMessageLevel.ERROR,
                                )
                            )

                test_measurement = SettlementRodMeasurement(
                    project=baec_project,
                    device=MeasurementDevice(
                        id_=measurement["Device name"],
                        qr_code=measurement["QR-code"],
                    ),
                    object_id=object_id,
                    date_time=datetime.strptime(
                        date_measurement, "%Y-%m-%dT%H:%M:%S"
                    ),
                    coordinate_reference_systems=coordinate_reference_systems,
                    rod_top_x=measurement["Coordinates Local"]["Easting"] or float("nan"),
                    rod_top_y=measurement["Coordinates Local"]["Northing"] or float("nan"),
                    rod_top_z=measurement["Coordinates Local"]["Height"] or float("nan"),
                    rod_length=measurement["Vertical offset (meters)"] or float("nan"),
                    rod_bottom_z=measurement["Coordinates Soil"]["Height groundplate"] or float("nan"),
                    ground_surface_z=measurement["Coordinates Soil"]["Height Soil"] or float("nan"),
                    status_messages=status_messages,
                    temperature=measurement["Temperature (Celsius)"] or float("nan"),
                    voltage=measurement["Voltage Locator One (mV)"] or float("nan"),
                )

                list_SettlementRodMeasurement.append(test_measurement)

        elif project in self.dic_projects:
            raise ValueError(
                f"{project} is in the project list, but not rod_id: {rod_id}"
            )
        else:
            raise ValueError(f"{project} is not in the project list")

        return SettlementRodMeasurementSeries(list_SettlementRodMeasurement)

    @staticmethod
    def convert_epsg_string_to_list_int(epsg_string: str) -> list:
        """
        Converts a Basetime coordinate projection to a list of string containing the EPSG codes.

        Input: Basetime coordinate string (for example: "RDNAPTrans (28992,5709)")

        Output: list of EPSG numbers (for example: [28992,5709])

        If list has a length of 2, XY and Z projection are present.
        If the list has a length of 1, only the XY projection is present.
        If the list is empty, no projection could be transformed.
        """
        pattern = r"\((\d+)(?:,(\d+))?\)"
        matches = re.findall(pattern, epsg_string)

        if matches:
            if matches[0][1]:
                num1, num2 = map(int, matches[0])
                return [num1, num2]
            else:
                num1 = int(matches[0][0])
                return [num1]
        else:
            return []
