from __future__ import annotations

import getpass
import json
import os
import re
from datetime import datetime
from os import PathLike
from typing import Dict, List

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

try:
    import boto3
    from botocore import exceptions
except ImportError as e:
    raise ImportError(
        "Please make sure that you installed baec with the correct extension. "
        f"Use pip install baec[aws] to use this model. {e}"
    )


class Credentials:
    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ) -> None:
        """
        Credentials needs to refer to the AWS credential file given by Basetime.

        Parameters
        ----------
        aws_access_key_id: str, optional
            The access key to use when creating the client.This is entirely optional, and if not provided,
            the credentials configured for the session will automatically be used. You only need to provide
            this argument if you want to override the credentials used for this specific client.
        aws_secret_access_key: : str, optional
            The secret key to use when creating the client.  Same semantics as aws_access_key_id above.
        """
        if aws_access_key_id is None:
            if "BASETIME_KEY_ID" not in os.environ:
                self.aws_access_key_id = input(
                    "Authentication is needed. What is your BaseTime key ID?"
                )
            else:
                self.aws_access_key_id = os.environ["BASETIME_KEY_ID"]
        else:
            self.aws_access_key_id = aws_access_key_id

        if aws_secret_access_key is None:
            if "BASETIME_ACCESS_KEY" not in os.environ:
                self.aws_secret_access_key = getpass.getpass("What is your access key?")
            else:
                self.aws_secret_access_key = os.environ["BASETIME_ACCESS_KEY"]
        else:
            self.aws_secret_access_key = aws_secret_access_key

    @classmethod
    def from_csv(
        cls,
        filepath_or_buffer: str
        | PathLike[str]
        | ReadCsvBuffer[bytes]
        | ReadCsvBuffer[str],
    ) -> "Credentials":
        """
        Any valid string path is acceptable. Credentials needs to refer to the AWS credential file given by Basetime.

        Parameters
        ----------
        filepath_or_buffer: filepath_or_buffer: str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str]

        Returns
        -------
        Credentials

        Raises
        ------
        ValueError/ClientError
            If the provided credential file does not contain the correct credentials.
            If the wrong type of value is given for the credential file.
        TypeError
            If the credential file does not contain credentials.
        ValueError
            If the list of measurements is empty.
            If the measurements are not for the same project, device or object.
        IOError
            If ZBASE file cannot be parsed by Pandas
        FileNotFoundError
            If filepath_or_buffer is requested but doesn't exist.

        """
        # Read the credentials file
        try:
            dict_credentials = pd.read_csv(filepath_or_buffer).to_dict("records")[0]
        except pd.errors.ParserError as e:
            raise IOError(
                f"Errors encountered while parsing contents of the credentials file: \n {e}"
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(e)
        except ValueError:
            raise ValueError(
                "Wrong type of credentials file given, str | PathLike[str] | ReadCsvBuffer[bytes] | "
                "ReadCsvBuffer[str], Any valid string path is acceptable."
            )
        return cls(
            dict_credentials["Access key ID"], dict_credentials["Secret access key"]
        )


class BaseTimeBucket:
    """
    Class object to get a list of projects and Point IDs or to import measurements as a SettlementRodMeasurementSeries.
    """

    def __init__(
        self,
        credentials: Credentials,
        s3bucket: str = "baec",
    ) -> None:
        """
        Initializes a ProjectsIDs object.

        Parameters
        ----------
        credentials : Credentials
            Any valid string path is acceptable. Credentials needs to refer to the AWS credential file given by Basetime.
        s3bucket : str
            Name of the bucket where data is stored. DEFAULT is 'baec'

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

        # Create boto3 client and resource for connecting to AWS S3
        s3c = boto3.client(
            service_name="s3",
            region_name="ca-central-1",
            aws_access_key_id=credentials.aws_access_key_id,
            aws_secret_access_key=credentials.aws_secret_access_key,
        )
        s3r = boto3.resource(
            service_name="s3",
            region_name="ca-central-1",
            aws_access_key_id=credentials.aws_access_key_id,
            aws_secret_access_key=credentials.aws_secret_access_key,
        )

        # Create the dictionary to translate the error codes. Get the error_codes file from the AWS S3 bucket
        dict_errors = {}
        try:
            for line in (
                s3r.Object(s3bucket, "error_codes.txt")
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
        except exceptions.ClientError:
            raise ValueError(
                "The AWS Access Key ID you provided does not exist in our records."
            )

        # Test the AWS S3 connection, load the list objects for projects the credential file can access
        try:
            list_projects = s3c.list_objects(Bucket=s3bucket, Prefix="", Delimiter="/")[
                "CommonPrefixes"
            ]
        except exceptions.ClientError:
            raise ValueError(
                "The AWS Access Key ID or Access Key Password you provided does not exist in our records."
            )

        # Iterate through all the folders in the S3 environment. The environment has the following folder structure:
        # - Company name
        #     - Folder with years in YYYY
        #         - Folder with days in MMDD
        #             - Measurements for each project.
        #
        # Read each object and write down the Point ID and Project name.
        for project in list_projects:
            dic_projects_ids: Dict[str, List[str]]
            dic_projects_ids = {}
            year_folders = s3c.list_objects(
                Bucket=s3bucket, Prefix=project["Prefix"], Delimiter="/"
            )
            for year in year_folders["CommonPrefixes"]:
                day_folders = s3c.list_objects(
                    Bucket=s3bucket, Prefix=year["Prefix"], Delimiter="/"
                )
                for day in day_folders["CommonPrefixes"]:
                    files = s3c.list_objects(
                        Bucket=s3bucket, Prefix=day["Prefix"], Delimiter="/"
                    )
                    for file in files["Contents"]:
                        if file["Key"] == day["Prefix"]:
                            continue
                        obj = s3r.Object(s3bucket, file["Key"])
                        json_dict = json.load(obj.get()["Body"])
                        if json_dict["Project"] not in dic_projects_ids:
                            dic_projects_ids[json_dict["Project"]] = []
                        for measurement in json_dict["Measurements"]:
                            if (
                                measurement["Point ID"]
                                not in dic_projects_ids[json_dict["Project"]]
                            ):
                                dic_projects_ids[json_dict["Project"]].append(
                                    measurement["Point ID"]
                                )
            dic_user_projects_points[project["Prefix"][:-1]] = dic_projects_ids

        # Initialize all attributes
        self.dic_projects = dic_user_projects_points
        self.s3c = s3c
        self.s3r = s3r
        self.s3bucket = s3bucket
        self.dict_errors = dict_errors

    def get_users_projects_ids(self) -> dict:
        """
        Return the dictionary containing every User as a key, then the Project as key, the value is a list of all the Point IDs.
        - Company/user
            - projects
                - point IDs
        """
        return self.dic_projects

    def make_settlement_rod_measurement_series(
        self, company: str, project: str, rod_id: str
    ) -> SettlementRodMeasurementSeries:
        """
        Make a SettlementRodMeasurementSeries:

        Initialize by checking if the values are inside the S3 environment of Basetime, by using variable [dic_projects].
        Iterate through all the folders in the S3 environment. The environment has the following folder structure:
        - Company name
            - Folder with years in YYYY
                - Folder with days in MMDD
                    - Measurements for each project.
                    If Point ID matches rod_id, copy measurement to a SettlementRodMeasurement class

        SettlementRodMeasurement creating:
            - Split Basetime EPSG code to list of EPSG numbers to add to CoordinateReferenceSystems
            - Split error codes into multiple StatusMessage classes
            - Add all values to the SettlementRodMeasurement class

        Parameters
        ----------
        company: str
            company name
        project: str
            project name
        rod_id: str
            settlement rod id as found in BaseTime platform.

        Returns
        -------
        SettlementRodMeasurementSeries
        """
        if (
            company in self.dic_projects
            and project in self.dic_projects[company]
            and rod_id in self.dic_projects[company][project]
        ):
            list_settlement_rod_measurement = []

            year_folders = self.s3c.list_objects(
                Bucket=self.s3bucket, Prefix=company + "/", Delimiter="/"
            )
            for year in year_folders["CommonPrefixes"]:
                day_folders = self.s3c.list_objects(
                    Bucket=self.s3bucket, Prefix=year["Prefix"], Delimiter="/"
                )
                for day in day_folders["CommonPrefixes"]:
                    files = self.s3c.list_objects(
                        Bucket=self.s3bucket, Prefix=day["Prefix"], Delimiter="/"
                    )
                    for file in files["Contents"]:
                        if project not in file["Key"]:
                            continue
                        obj = self.s3r.Object(self.s3bucket, file["Key"])
                        json_dict = json.load(obj.get()["Body"])
                        for measurement in json_dict["Measurements"]:
                            if measurement["Point ID"] == rod_id:
                                list_epsg_codes = self.convert_epsg_string_to_list_int(
                                    measurement["Coordinate projection"]
                                )

                                if len(list_epsg_codes) == 2:
                                    coordinate_reference_systems = (
                                        CoordinateReferenceSystems(
                                            pyproj.CRS.from_user_input(
                                                list_epsg_codes[0]
                                            ),
                                            pyproj.CRS.from_user_input(
                                                list_epsg_codes[1]
                                            ),
                                        )
                                    )
                                elif len(list_epsg_codes) == 1:
                                    coordinate_reference_systems = (
                                        CoordinateReferenceSystems(
                                            pyproj.CRS.from_user_input(
                                                list_epsg_codes[0]
                                            ),
                                            pyproj.CRS.from_user_input(
                                                list_epsg_codes[0]
                                            ),
                                        )
                                    )
                                else:
                                    coordinate_reference_systems = (
                                        CoordinateReferenceSystems(None, None)
                                    )

                                if measurement["Comments Project"] == "No comment":
                                    status_messages = [
                                        StatusMessage(
                                            code=7000,
                                            description="Measurement approved",
                                            level=StatusMessageLevel.OK,
                                        )
                                    ]
                                else:
                                    status_messages = []
                                    error_string_list = measurement[
                                        "Comments Project"
                                    ].split(",")
                                    error_integer_list = [
                                        int(num) for num in error_string_list
                                    ]
                                    for error_code in error_integer_list:
                                        if (
                                            self.dict_errors[error_code][
                                                "status message level"
                                            ]
                                            == "INFO"
                                        ):
                                            status_messages.append(
                                                StatusMessage(
                                                    code=error_code,
                                                    description=self.dict_errors[
                                                        error_code
                                                    ]["description"],
                                                    level=StatusMessageLevel.INFO,
                                                )
                                            )
                                        elif (
                                            self.dict_errors[error_code][
                                                "status message level"
                                            ]
                                            == "WARNING"
                                        ):
                                            status_messages.append(
                                                StatusMessage(
                                                    code=error_code,
                                                    description=self.dict_errors[
                                                        error_code
                                                    ]["description"],
                                                    level=StatusMessageLevel.WARNING,
                                                )
                                            )
                                        elif (
                                            self.dict_errors[error_code][
                                                "status message level"
                                            ]
                                            == "ERROR"
                                        ):
                                            status_messages.append(
                                                StatusMessage(
                                                    code=error_code,
                                                    description=self.dict_errors[
                                                        error_code
                                                    ]["description"],
                                                    level=StatusMessageLevel.ERROR,
                                                )
                                            )

                                test_measurement = SettlementRodMeasurement(
                                    project=Project(
                                        id_=json_dict["Project_uuid"],
                                        name=json_dict["Project"],
                                    ),
                                    device=MeasurementDevice(
                                        id_=measurement["Locator One ID"],
                                        qr_code=measurement["QR Code"],
                                    ),
                                    object_id=measurement["Point ID"],
                                    date_time=datetime.strptime(
                                        json_dict["Date"][:19], "%Y-%m-%d %H:%M:%S"
                                    ),
                                    coordinate_reference_systems=coordinate_reference_systems,
                                    rod_top_x=measurement["Coordinates ARP"]["X"]
                                    or float("nan"),
                                    rod_top_y=measurement["Coordinates ARP"]["Y"]
                                    or float("nan"),
                                    rod_top_z=measurement["Coordinates ARP"]["Z"]
                                    or float("nan"),
                                    rod_length=measurement["Vertical Offset (Meter)"]
                                    or float("nan"),
                                    rod_bottom_z=measurement["Height ground level"][
                                        "Zuncorrected"
                                    ]
                                    or float("nan"),
                                    ground_surface_z=measurement["Coordinates ARP"][
                                        "Soil level"
                                    ]
                                    or float("nan"),
                                    status_messages=status_messages,
                                    temperature=measurement["Temperature (Celsius)"]
                                    or float("nan"),
                                    voltage=measurement["Voltage Locator One (mV)"]
                                    or float("nan"),
                                )

                                list_settlement_rod_measurement.append(test_measurement)

        elif company in self.dic_projects and project in self.dic_projects[company]:
            raise ValueError(
                f"{company} is in the user list and {project} is in the project list, but not rod_id: {rod_id}"
            )
        elif company in self.dic_projects:
            raise ValueError(
                f"{company} is in the user list, but not the project: {project}"
            )
        else:
            raise ValueError(f"{company} is not in the user list")

        return SettlementRodMeasurementSeries(list_settlement_rod_measurement)

    @staticmethod
    def convert_epsg_string_to_list_int(epsg_string: str) -> list:
        """
        Converts a Basetime coordinate projection to a list of string containing the EPSG codes.

        If list has a length of 2, XY and Z projection are present.
        If the list has a length of 1, only the XY projection is present.
        If the list is empty, no projection could be transformed.

        Parameters
        ----------
        epsg_string: str
            Basetime coordinate string (for example: "RDNAPTrans (28992,5709)")

        Returns
        -------
        list of EPSG numbers (for example: [28992,5709])
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
