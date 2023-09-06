import json
import os
import sys
from dataclasses import dataclass


from pyspark.sql import SparkSession

@dataclass
class SparkBaseStage():
    base_name : str = 'pyspark_base_name'
    version : str = "v0.0"
    timestamp : str = ""
    stage_name : str = ''
    spark_jars : str = ''
    # spark_jars : str = 'gs://ds-spark-staging-area/data-pipelines/artifacts/demo/data-pipelines-assembly-0.1.1-SNAPSHOT.jar'
    pyfiles : str = None
    venv : str = None
    stage_config: dict = None
    spark: SparkSession = None

    def __post_init__(self):
        self.bucket_name = self.stage_config['bucket_name']
        self.project_id = self.stage_config['project_id']
        self.project_name = self.stage_config['project_name']
        self.region = self.stage_config['region']
        self.unique_iteration_id = self.stage_config['unique_iteration_id']

        self.user_id = ''
        if 'user_id' in self.stage_config:
            self.user_id = self.stage_config['user_id']

        if self.unique_iteration_id:
            self.folder_path = self.project_name + self.user_id + \
                               '/unique_iteration_id_' + self.unique_iteration_id
        else:
            self.folder_path = self.project_name + self.user_id + '/main'

        self.bucket_path = f's3://{self.bucket_name}/{self.folder_path}'
        self.start_date = ""
        self.end_date = ""
        self.extra_params = ""

    def google__post_init__(self):
        self.bucket_name = self.stage_config['bucket_name']
        self.project_id = self.stage_config['project_id']
        self.project_name = self.stage_config['project_name']
        self.region = self.stage_config['region']
        self.unique_iteration_id = self.stage_config['unique_iteration_id']

        self.user_email = ''
        if 'user_email' in self.stage_config:
            self.user_email = '/' + self.stage_config['user_email']

        if self.unique_iteration_id:
            self.folder_path = self.project_name + self.user_email + \
                               '/unique_iteration_id_' + self.unique_iteration_id
        else:
            self.folder_path = self.project_name + self.user_email + '/main'

        self.bucket_path = f's3://{self.bucket_name}/{self.folder_path}'
        self.start_date = ""
        self.end_date = ""
        self.extra_params = ""

    def read_bigquery(self, query):
        from google.cloud import bigquery

        bq = bigquery.Client()

        print('Querying BigQuery')
        query_job = bq.query(query)

        # Wait for query execution
        query_job.result()

        df = self.spark.read.format('bigquery') \
            .option('dataset', query_job.destination.dataset_id) \
            .load(query_job.destination.table_id)
        return df

    def load(self):
        # self.load_config()
        pass

    def run(self):
        pass

    def store(self):
        pass

    def __call__(self, *args, **kwargs):
        print(f"Start stage - {self.stage_name}  === {self} ===")
        self.load()
        print(f"Done load - {self.stage_name}")
        self.run()
        print(f"Done run  - {self.stage_name}")
        self.store()
        print(f"End stage - {self.stage_name}")

