from gaiaframework.base.batch.spark_base_stage import SparkBaseStage
from dataclasses import dataclass

@dataclass
class SetDataStage(SparkBaseStage):
    base_name: str = 'pyspark_{name-your-service}_set_data'
    csv_path: str = "None"
    output_path: str = "None"

    def load(self):
        print(self)

    def run(self):
        spark = self.spark

        input_parquet_name = f"highest_prices_{self.project_id}"

        page_list = spark.read.parquet(f"{self.output_path}/{input_parquet_name}.parquet")
        page_list.printSchema()
        page_list.show(5)

        page_list.write.mode("overwrite").parquet(f"{self.output_path}/{input_parquet_name}_set_data_results.parquet")
