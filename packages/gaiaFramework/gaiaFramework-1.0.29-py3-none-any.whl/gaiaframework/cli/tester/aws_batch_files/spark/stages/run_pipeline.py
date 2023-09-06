from gaiaframework.base.batch.spark_base_stage import SparkBaseStage
from dataclasses import dataclass
from typing import Iterator, List, Union
import pandas as pd
from pyspark.sql.types import *

from pipeline.schema.outputs import generatedProjectNameOutputs

@dataclass
class RunPipelineStage(SparkBaseStage):
    base_name: str = 'pyspark_{name-your-service}_run_pipeline'
    csv_path: str = "None"
    output_path: str = "None"

    udf_schema = StructType([StructField("id", IntegerType()),
                                  StructField("url", StringType()),
                                  StructField("res", StringType())])

    # def __init__(self, csv_path, output_path):
    #     self.csv_path = csv_path
    #     self.output_path = output_path

    def load(self):
        print(self)

    def run(self):
        spark_session = self.spark

        df = spark_session.createDataFrame([(1, 'http://aaa', "I"),
                                            (2, 'http://bbb', "am"),
                                            (3, 'http://ccc', "testing")], ("id", "url", "res"))
        df.show(3)
        out_df = df.mapInPandas(func=self.map_in_pandas, schema=self.udf_schema)
        out_df.show(1)

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

        # self.df = df