"""! @brief ZIDS_Stage base class for the batch stage class."""

import json
import sys
from pyspark.sql import SparkSession
from typing import List, Any

##
# @file
# @brief Defines stage base class.
class DS_Stage():
    def __init__(self, stage_config):
        """! ZIDS_Stage initializer.
        Loads config file.

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.

        """
        self.bucket_name = stage_config['bucket_name']
        self.project_id = stage_config['project_id']
        self.project_name = stage_config['project_name']
        self.region = stage_config['region']
        self.unique_iteration_id = stage_config['unique_iteration_id']

        self.user_email = ''
        if 'user_email' in stage_config:
            self.user_email = '/' + stage_config['user_email']

        if self.unique_iteration_id:
            self.folder_path = self.project_name + self.user_email + \
                               '/unique_iteration_id_' + self.unique_iteration_id
        else:
            self.folder_path = self.project_name + self.user_email + '/main'

        self.bucket_path = f'gs://{self.bucket_name}/{self.folder_path}'
        self.start_date = ""
        self.end_date = ""
        self.extra_params = ""

    def fix_bucket_path_for_s3(self, stage_config):
        self.user_id = ''
        if 'user_id' in stage_config:
            self.user_id = '/' + stage_config['user_id']

        if self.unique_iteration_id:
            self.folder_path = self.project_name + self.user_id + \
                               '/unique_iteration_id_' + self.unique_iteration_id
        else:
            self.folder_path = self.project_name + self.user_id + '/main'

        self.bucket_path = f's3://{self.bucket_name}/{self.folder_path}'
        print('self.bucket_path', self.bucket_path)

    def update_stage_params(self, start_date, end_date, params):
        """! Update start date
            Args:
                start_date: String, containing the starting date, received from Airflow
                end_date: String, containing the end date, received from Airflow
                params: String, containing extra parameters provided by user
        """
        print(f"{start_date = }, {end_date = }, {params = }")
        self.start_date = start_date
        self.end_date = end_date
        self.extra_params = params

    def main(self, **kwargs: Any):
        """! ZIDS_Stage main function.
        This function is the "entrypoint" for the stage, this will run when the job is executed.

            Args:
                **kwargs : Whatever is needed for the stage to run properly.
        """
        raise NotImplementedError

    def load_spark(self, jar=None) -> SparkSession:   # TODO: Generalize this in order to receive config options.
        """! Basic loading of a spark session.

            Returns:
                A basic spark session
        """
        spark_conf = SparkSession.builder \
            .appName(self.project_name) \
            .config('spark.ui.showConsoleProgress', True) \
            .config("spark.sql.parquet.compression.codec", "gzip")
        if jar:
            spark_conf.config('spark.jars', jar)

        spark = spark_conf.getOrCreate()

        print(f"Spark ID: {spark.sparkContext.applicationId}")
        return spark




