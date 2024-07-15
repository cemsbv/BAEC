from __future__ import annotations
from datetime import datetime
import pandas as pd
import boto3
import botocore
import json
import pyproj
import re
from typing import List

from baec.measurements.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.project import Project
from baec.measurements.settlement_rod_measurement import SettlementRodMeasurement, StatusMessage, StatusMessageLevel


class ProjectsIDs:

    """
    Class opject to get a list of projects and Point IDs or to import measurements as a SettlementRodMeasurementSeries
    """

    def __init__(self ,credentials : str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str], s3bucket : str = 'baec'):

        """
        Initializes a ProjectsIDs object

        Parameters
        ----------
        credentials : str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str],
            Any valid string path is acceptable. Credentials needs to refer to the AWS credential file given by Basetime.
        s3bucket : str
            Name of the bucket where data is stored. DEFAULT is 'baec'

        Returns
        -------
        series : ProjectsIDs [dict]
            A overview of all the avaiable project and connected settlement rods within every project. [dict]
            <Keys> : project names
            <Values> : list of Point ID's inside every project.

        series : SettlementRodMeasurementSeries
            A SettlementRodMeasurementSeries object for every available rod measurement, to be called within the class

        Raises
        ------
        ValueError/ClientError
            If the provided credentiual file does not contain the correct credentials.
            If the wrong type of value is given for the credential file.
        TypeError
            If the input types are incorrect.
            If the credential file does not contain credentials.
        ValueError
            If the list of measurements is empty.
            If the measurements are not for the same project, device or object.
        IOError
            If ZBASE file cannot be parsed by Pandas
        FileNotFoundError:
            If filepath_or_buffer is requested but doesnt exist.
        """

        dic_user_projects_points = {}

        #Read the credentials file
        try:
            dict_credentials = pd.read_csv(credentials).to_dict('records')[0]
        except pd.errors.ParserError as e:
            raise IOError(f"Errors encountered while parsing contents of the credentials file: \n {e}")
        except FileNotFoundError as e:
            raise FileNotFoundError(e)
        except ValueError as e:
            raise ValueError('Wrong type of credentials file given, str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str], Any valid string path is acceptable.')

        #Create boto3 client and resource for connecting to AWS S3.
        s3c = boto3.client(
            service_name='s3',
            region_name='ca-central-1',
            aws_access_key_id=dict_credentials['Access key ID'],
            aws_secret_access_key=dict_credentials['Secret access key']
        )
        s3r = boto3.resource(
            service_name='s3',
            region_name='ca-central-1',
            aws_access_key_id=dict_credentials['Access key ID'],
            aws_secret_access_key=dict_credentials['Secret access key']
        )

        #Create the dictionary to translate the error codes. Get the error_codes file from the AWS S3 bucket.
        dict_errors={}
        '''
        Get the error_codes.txt object from the Basetime S3 environment, read and split into a list of lines.
        Iterate through every line and add all the codes to a dictionary to be used for every measurement.
        '''
        try:
            for line in s3r.Object(s3bucket,'error_codes.txt').get()['Body'].read().decode('utf-8').split('\n'): #Get the AWS file from de S3 environment and read the file.
                error_line=line.split(',')
                dict_errors[int(error_line[0])]={'basetime error':error_line[1],'description':error_line[2],'status message level':error_line[3]}
        except botocore.exceptions.ClientError as e:
            raise ValueError('The AWS Access Key Id you provided does not exist in our records.')

        #Test the AWS S3 connection, load the list objects for projects the credential file can acces.
        try:
            list_projects = s3c.list_objects(Bucket=s3bucket, Prefix='', Delimiter='/')['CommonPrefixes']
        except botocore.exceptions.ClientError as e:
            raise ValueError('The AWS Access Key Id you provided does not exist in our records.')

        """
        Iterate through all the folders in the S3 environment. The environment has the following folder structur:
        -Company name
            -Folder with years in YYYY
                -Folder with days in MMDD
                    -Measurements for each project.
        
        Read each object and write down the Point ID and Project name
        """
        for project in list_projects:
            dic_projects_ids = {}
            year_folders = s3c.list_objects(Bucket=s3bucket, Prefix=project['Prefix'], Delimiter='/')
            for year in year_folders['CommonPrefixes']:
                day_folders = s3c.list_objects(Bucket=s3bucket, Prefix=year['Prefix'], Delimiter='/')
                for day in day_folders['CommonPrefixes']:
                    files = s3c.list_objects(Bucket=s3bucket, Prefix=day['Prefix'], Delimiter='/')
                    for file in files['Contents']:
                        #file key also returns the path to folder, which need to be skipped.
                        if file['Key']==day['Prefix']:
                            continue
                        #Load measurement file
                        obj=s3r.Object(s3bucket,file['Key'])
                        json_dict=json.load(obj.get()['Body'])
                        #Add project as [key] to dictionary is key does not excist
                        if json_dict['Project'] not in dic_projects_ids:
                            dic_projects_ids[json_dict['Project']]=[]
                        #For every measurement: add Point ID to list [value] if not already in list.
                        for measurement in json_dict['Measurements']:
                            if measurement['Point ID'] not in dic_projects_ids[json_dict['Project']]:
                                dic_projects_ids[json_dict['Project']].append(measurement['Point ID'])
            dic_user_projects_points[project['Prefix'][:-1]] = dic_projects_ids
        #Initialize all attributes
        self.dic_projects = dic_user_projects_points
        self.s3c = s3c
        self.s3r = s3r
        self.s3bucket = s3bucket
        self.dict_errors = dict_errors

    def get_users_projects_ids(self):
        """Return the dictionary containing every User as a key, then the Project as key, the value is a list of all the Point ID's
        -Company/user
            -projects
                -point IDs
        """
        return self.dic_projects
    
    def make_SettlementRodMeasurementSeries(self,company : str,project : str,rod_id : str):
        """
        Make a SettlementRodMeasurementSeries:

        Initialize by checking if the values are inside the S3 environment of Basetime, by using variable [dic_projects].
        Iterate through all the folders in the S3 environment. The environment has the following folder structur:
        -Company name
            -Folder with years in YYYY
                -Folder with days in MMDD
                    -Measurements for each project.
                    If Point ID matches rod_id, copy measurement to a SettlementRodMeasurement class

        SettlementRodMeasurement creating:
            - Split Basetime epsg code to list of epsg number to add to CoordinateReferenceSystems
            - Split error codes into multiple StatusMessage classes
            - Add all values to the SettlementRodMeasurement class

        """
        if company in self.dic_projects and project in self.dic_projects[company] and rod_id in self.dic_projects[company][project]:

            list_SettlementRodMeasurementSeries=[]

            year_folders = self.s3c.list_objects(Bucket=self.s3bucket, Prefix=company+'/', Delimiter='/')
            for year in year_folders['CommonPrefixes']:
                day_folders = self.s3c.list_objects(Bucket=self.s3bucket, Prefix=year['Prefix'], Delimiter='/')
                for day in day_folders['CommonPrefixes']:
                    files = self.s3c.list_objects(Bucket=self.s3bucket, Prefix=day['Prefix'], Delimiter='/')
                    for file in files['Contents']:
                        if project not in file['Key']:
                            continue
                        obj=self.s3r.Object(self.s3bucket,file['Key'])
                        json_dict=json.load(obj.get()['Body'])
                        for measurement in json_dict['Measurements']:
                            if measurement['Point ID']==rod_id:
                                '''
                                Set all the object needed to make a measurement series
                                '''

                                #Make the CoordinateReferenceSystems by extracting the epsg codes from the Coordinate projection string of Basetime
                                list_epsg_codes=self.convert_epsg_string_to_list_int(measurement['Coordinate projection'])

                                if len(list_epsg_codes)==2:
                                    coordinate_reference_systems = CoordinateReferenceSystems(pyproj.CRS.from_user_input(list_epsg_codes[0]),pyproj.CRS.from_user_input(list_epsg_codes[1]))
                                elif len(list_epsg_codes)==1:
                                    coordinate_reference_systems = CoordinateReferenceSystems(pyproj.CRS.from_user_input(list_epsg_codes[0]),pyproj.CRS.from_user_input(list_epsg_codes[0]))
                                else:
                                    coordinate_reference_systems = CoordinateReferenceSystems(None)

                                if measurement['Comments Project']=='No comment':
                                    status_messages = [StatusMessage(code=7000,description='Measurement approved',level=StatusMessageLevel.OK)]
                                else:
                                    status_messages=[]
                                    #Make the StatusMessage, by using the list of integers from basetime.
                                    error_string_list = measurement['Comments Project'].split(',')
                                    # Convert each string in the list to an integer using list comprehension
                                    error_integer_list = [int(num) for num in error_string_list]
                                    for error_code in error_integer_list:
                                        if self.dict_errors[error_code]['status message level']=='INFO':
                                            status_messages.append(StatusMessage(code=error_code,description=dict_errors[error_code]['description'],level=StatusMessageLevel.INFO))
                                        if self.dict_errors[error_code]['status message level']=='WARNING':
                                            status_messages.append(StatusMessage(code=error_code,description=dict_errors[error_code]['description'],level=StatusMessageLevel.WARNING))
                                        if self.dict_errors[error_code]['status message level']=='ERROR':
                                            status_messages.append(StatusMessage(code=error_code,description=dict_errors[error_code]['description'],level=StatusMessageLevel.ERROR))


                                measurement=self.replace_null_to_nan_in_dict(measurement)
                                test_measurement = SettlementRodMeasurement(
                                project     =   Project(id_='1234',name=json_dict['Project']),
                                device      =   (MeasurementDevice(id_ = measurement['Locator One ID'], qr_code=measurement['QR Code'])),
                                object_id   =   measurement['Point ID'],
                                date_time   =   datetime.strptime(json_dict['Date'][:19],'%Y-%m-%d %H:%M:%S'),
                                coordinate_reference_systems    =   coordinate_reference_systems,
                                rod_top_x   =   measurement['Coordinates ARP']['X'],
                                rod_top_y   =   measurement['Coordinates ARP']['Y'],
                                rod_top_z   =   measurement['Coordinates ARP']['Z'],
                                rod_length  =   measurement['Vertical Offset (Meter)'],
                                rod_bottom_z=   measurement['Height ground level']['Zuncorrected'],
                                ground_surface_z    =   measurement['Coordinates ARP']['Soil level'],
                                status_messages =    status_messages,
                                temperature =   measurement['Temperature (Celsius)'],
                                voltage     =   measurement['Voltage Locator One (mV)']
                                )

                                list_SettlementRodMeasurementSeries.append(test_measurement)

        elif company in self.dic_projects and project in self.dic_projects[company]:
            raise ValueError(f"{company} is in de user list and {project} is in the project list, but not rod_id: {rod_id}")
        elif company in self.dic_projects:
            raise ValueError(f"{company} is in de user list, but not the project: {project}")
        else:
            raise ValueError(f"{company} is not in the user list")

        return list_SettlementRodMeasurementSeries


    '''
    Replaces None values to float values, in a json_dict['Measurements'] dictionary. Only works with the provided JSON file from Basetime.
    '''
    def replace_null_to_nan_in_dict(self, dictionary : dict):
        if dictionary['Coordinates ARP']['X'] is None:
            dictionary['Coordinates ARP']['X']=float('nan')
        if dictionary['Coordinates ARP']['Y'] is None:
            dictionary['Coordinates ARP']['Y']=float('nan')
        if dictionary['Coordinates ARP']['Z'] is None:
            dictionary['Coordinates ARP']['Z']=float('nan')
        if dictionary['Coordinates ARP']['Soil level'] is None:
            dictionary['Coordinates ARP']['Soil level']=float('nan')
        if dictionary['Vertical Offset (Meter)'] is None:
            dictionary['Vertical Offset (Meter)']=float('nan')
        if dictionary['Height ground level']['Zuncorrected'] is None:
            dictionary['Height ground level']['Zuncorrected']=float('nan')
        if dictionary['Height ground level']['Zcorrected'] is None:
            dictionary['Height ground level']['Zcorrected']=float('nan')
        if dictionary['Temperature (Celsius)'] is None:
            dictionary['Temperature (Celsius)']=float('nan')
        if dictionary['Voltage Locator One (mV)'] is None:
            dictionary['Voltage Locator One (mV)']=float('nan')
        return dictionary


    def convert_epsg_string_to_list_int(self, espg_string : str):
        '''
        Converts a Basetime coordinate projection to a list of string containing the epsg codes 
        
        Input: Basetime coordinate string (for example: "RDNAPTrans (28992,5709)")

        Output: list of epsg number (for example: [28992,5709])

        If list has a lenght of 2, XY and Z projection are present
        If the list has a lenght of 1, only the XY projection is present
        If the list is empty, no projection could be transformed.
        '''
        # Define the regex pattern to match numbers within parentheses, with optional second number
        pattern = r'\((\d+)(?:,(\d+))?\)'

        matches = re.findall(pattern, espg_string)

        # If matches are found, re.findall() returns a list of tuples
        if matches:
            if matches[0][1]:  # If the second number is present
                num1, num2 = map(int, matches[0])  # Convert the matched strings to integers
                return [num1, num2]
            else:  # Only the first number is present
                num1 = int(matches[0][0])
                return [num1]
        else:
            return []
