from gaiaframework.base.batch.spark_base_stage import SparkBaseStage
from dataclasses import dataclass

@dataclass
class GetDataStage(SparkBaseStage):
    base_name: str = 'pyspark_{name-your-service}_get_data'
    csv_path: str = "None"
    output_path: str = "None"

    # def __init__(self, csv_path, output_path):
    #     self.csv_path = csv_path
    #     self.output_path = output_path

    def load(self):
        print(self)

    def run(self):
        spark = self.spark

        df = spark.read.options(header='true', inferSchema='true').csv(self.csv_path)

        df.printSchema()
        df.createOrReplaceTempView("sales")
        highest_price_unit_df = spark.sql("select * from sales where UnitPrice >= 3.0")
        # highestPriceUnitDF.write.parquet("s3://us-east1-test-4ba22677-bucket/data/highest_prices.parquet")
        highest_price_unit_df.write.mode("overwrite").parquet(f"{self.output_path}/highest_prices_{self.project_id}.parquet")

        # self.df = df