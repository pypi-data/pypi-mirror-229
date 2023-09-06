"""! @brief Run pipeline stage, which will run the project's pipeline on the retrieved data."""
import sys
import pandas as pd
from typing import Any, Union, List
from json import loads as json_loads
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from typing import Iterator

from gaiaframework.base.batch.stage_base import DS_Stage

from pipeline.schema.outputs import generatedProjectNameOutputs

from aws_batch_files.spark.spark_pipeline import SparkPipeline


##
# @file
# @brief Stage main class, implements ZIDS_Stage base class.
class RunPipelineStage(DS_Stage):
    """! Stage class

    Implement a stage that will later be converted to an executable job in a specific workflow.
    """

    def __init__(self, stage_config):
        """! The Stage class (RunPipelineStage) initializer.
        Base class will load basic configuration parameters, additional fields should be added here.

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(stage_config)
        self.fix_bucket_path_for_s3(stage_config)
        self.udf_schema = StructType([StructField("id", IntegerType()),
                                      StructField("url", StringType()),
                                      StructField("res", StringType())])

    def get_stage_name(self):
        """! Get the stage name

            Returns:
                A string, containing the stage's name
        """
        return self.__class__.__name__

    @staticmethod
    def map_in_pandas(partition: Iterator[pd.DataFrame]):
        """! Executes the project main pipeline

                Args:
                    partition: Iterator[pd.DataFrame], we get an iterator to a Pandas dataframe, on which
                    we can perform actions, such as running the project pipeline and writing the output
        """
        def test():
            from pipeline.pipeline import generatedProjectNamePipeline
            p = generatedProjectNamePipeline()
            pipeline_output = p.execute()
            return pipeline_output

        for pdf in partition:
            pdf_output: Union[generatedProjectNameOutputs, List[generatedProjectNameOutputs]] = test()
            print(f'output: {pdf_output}')
            pdf.at[0, 'res'] = pdf_output.version
            yield pdf[pdf.id == 2]

    def main(self, **kwargs: Any):
        """! Executes the main functionality of the stage.

            Args:
                **kwargs : Whatever is needed for the stage to run properly.
        """
        spark_session = self.load_spark()
        df = spark_session.createDataFrame([(1, 'http://aaa', "I"),
                                            (2, 'http://bbb', "am"),
                                            (3, 'http://ccc', "testing")], ("id", "url", "res"))
        df.show(3)
        out_df = df.mapInPandas(func=self.map_in_pandas, schema=self.udf_schema)
        out_df.show(1)


if __name__ == "__main__":
    """! Executes the stage by instantiating it and calling the main function.
    Set up argument condition according to the usage of the written stage

        Args:
            System argument 1 - Configuration file
            System argument 2 - Start date
    """
    if sys.argv and len(sys.argv) > 1:
        config = json_loads(sys.argv[1])
        stage = RunPipelineStage(config)
        try:
            start_date = sys.argv[2]
            end_date = sys.argv[3]
            params = json_loads(sys.argv[4])
            stage.update_stage_params(start_date, end_date, params)
            spark_stage_config = {
                'csv_path': f's3://{stage.bucket_name}/example_data/retail_day.csv',
                'output_path': f'{stage.bucket_path}/example_data'
            }
            spark_pipeline = SparkPipeline(spark_stage_config=spark_stage_config, stage_config=config)
            spark_pipeline.run_stage('run_pipeline')
        except Exception as e:
            raise Exception(f" Stage failed with error: {e}")
    else:
        raise Exception(f"Stage configuration not provided, Can't run stage")


