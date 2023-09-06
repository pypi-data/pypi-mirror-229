import os
import sys
import json
from typing import Dict
from datetime import datetime
from gaiaframework.base.batch.spark_base_stage import SparkBaseStage

from aws_batch_files.spark.stages.get_data import GetDataStage
from aws_batch_files.spark.stages.run_pipeline import RunPipelineStage
from aws_batch_files.spark.stages.set_data import SetDataStage
from pyspark.sql import SparkSession
import time

class SparkPipeline():
    base_path = ''
    stage_config: dict = None
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def __init__(self, spark_stage_config, stage_config):
        self.spark_stage_config = spark_stage_config
        self.stage_config = stage_config
        self.stages: Dict[str, SparkBaseStage] = {
            "get_data": GetDataStage(
                csv_path=self.spark_stage_config['csv_path'],
                output_path=self.spark_stage_config['output_path'],
                stage_config=self.stage_config
            ),
            "run_pipeline": RunPipelineStage(
                csv_path=self.spark_stage_config['csv_path'],
                output_path=self.spark_stage_config['output_path'],
                stage_config=self.stage_config
            ),
            "set_data": SetDataStage(
                csv_path=self.spark_stage_config['csv_path'],
                output_path=self.spark_stage_config['output_path'],
                stage_config=self.stage_config
            )
        }
        self.spark = SparkSession.builder \
            .appName(type(self).__name__) \
            .config('spark.ui.showConsoleProgress', True) \
            .config("spark.sql.parquet.compression.codec", "gzip") \
            .getOrCreate()

        hadoop_version = self.spark.version
        print("Hadoop version:", hadoop_version)

        for stage in self.stages:
            self.stages[stage].stage_name = stage
            # self.stages[stage].base_name = self.base_name
            self.stages[stage].timestamp = self.timestamp
            self.stages[stage].spark = self.spark
            # self.stages[stage].config = config_stage

    def run_stage(self, stage_name: str):
        print("Running stage: %s" % stage_name)
        stage = self.stages[stage_name]
        start_time = time.time()
        stage.stage_name = stage_name
        stage()
        time_took = round(time.time() - start_time, 2)
        print("Stage completed in: %0.1f min" % (time_took / 60.0))
        return stage_name

    def run_all(self) -> None:
        print("Start run ALL")
        for stage in self.stages:
            self.run_stage(stage)
        print("End run ALL")


if __name__ == "__main__":

    file_path = os.path.dirname(os.path.abspath(__file__))
    curr_path = file_path[:file_path.rfind("aws_batch_files")]
    sys.path.append(curr_path)

    spark_stage_config = {
        'csv_path': '../../retail_day.csv',
        'output_path': '../../',
    }

    with open(curr_path + '/aws_batch_files/batch_config.json') as batch_cfg_file:
        stage_config = json.load(batch_cfg_file)
    spark_pipeline = SparkPipeline(spark_stage_config=spark_stage_config, stage_config=stage_config)
    spark_pipeline.run_all()
