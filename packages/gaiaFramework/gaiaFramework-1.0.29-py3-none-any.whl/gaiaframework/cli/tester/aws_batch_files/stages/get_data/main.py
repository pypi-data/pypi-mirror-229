"""! @brief Get Data stage, for obtaining data from a generic source, such as a database."""
import sys
from typing import Any
from json import loads as json_loads
from pyspark.sql import SparkSession
from pyspark import __version__ as pyspark_version
import platform

from gaiaframework.base.batch.stage_base import DS_Stage

print('platform.python_version()', platform.python_version())
print('pyspark_version', pyspark_version)

from aws_batch_files.spark.spark_pipeline import SparkPipeline


##
# @file
# @brief Stage main class, implements ZIDS_Stage base class.
class GetDataStage(DS_Stage):
    """! Stage class

    Implement a stage that will later be converted to an executable job in a specific workflow.
    """

    def __init__(self, stage_config):
        """! The Stage class (generatedStageName) initializer.
        Base class will load basic configuration parameters, additional fields should be added here

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.
        """

        ##
        # @hidecallgraph @hidecallergraph
        print(f"Initializing Stage: {self.get_name()}")
        super().__init__(stage_config)
        self.fix_bucket_path_for_s3(stage_config)
        self.start_date = ""

    def get_name(self):
        """! Get the stage name
        """
        return self.__class__.__name__


if __name__ == "__main__":
    """! Executes the stage by instantiating it and calling the main function.
    Set up argument condition according to the usage of the written stage

        Args:
            System argument 1 - Configuration file
            System argument 2 - Start date
    """
    if sys.argv and len(sys.argv) > 1:
        config = json_loads(sys.argv[1])
        stage = GetDataStage(config)
        try:
            start_date = sys.argv[2]
            end_date = sys.argv[3]
            params = json_loads(sys.argv[4])
            print('config', config)
            print('start_date', start_date)
            print('end_date', end_date)
            print('params', params)
            stage.update_stage_params(start_date, end_date, params)
            spark_stage_config = {
                'csv_path': f's3://{stage.bucket_name}/example_data/retail_day.csv',
                'output_path': f'{stage.bucket_path}/example_data'
            }
            spark_pipeline = SparkPipeline(spark_stage_config=spark_stage_config, stage_config=config)
            spark_pipeline.run_stage('get_data')
        except Exception as e:
            raise Exception(f" Stage failed with error: {e}")
    else:
        raise Exception(f"Stage configuration not provided, Can't run stage")


