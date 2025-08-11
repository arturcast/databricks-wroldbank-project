from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from src.common.config import TABLE_BRONZE, TABLE_SILVER, CATALOG, SCHEMA
from src.common.validation import valid_country_iso3, valid_year

schema_obs = StructType([
    StructField("indicator", StructType([
        StructField("id", StringType()),
        StructField("value", StringType())
    ])),
    StructField("country", StructType([
        StructField("id", StringType()),
        StructField("value", StringType())
    ])),
    StructField("countryiso3code", StringType()),
    StructField("date", StringType()),
    StructField("value", DoubleType()),
    StructField("unit", StringType()),
    StructField("obs_status", StringType()),
    StructField("decimal", IntegerType())
])

def main():
    spark = SparkSession.builder.appName("wb-silver-transform").getOrCreate()
    spark.sql(f"USE CATALOG {CATALOG}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
    spark.sql(f"USE {CATALOG}.{SCHEMA}")
    bronze = spark.table(TABLE_BRONZE)
    parsed = bronze.select(
        F.from_json(F.col("payload"), schema_obs).alias("j"),
        "indicator_id",
        "ingestion_ts"
    )
    flat = parsed.select(
        F.col("indicator_id").alias("indicator_id"),
        F.col("j.indicator.id").alias("indicator_code"),
        F.col("j.indicator.value").alias("indicator_name"),
        F.col("j.country.id").alias("country_code2"),
        F.col("j.country.value").alias("country_name"),
        F.col("j.countryiso3code").alias("country_iso3"),
        F.col("j.date").alias("year_str"),
        F.col("j.value").cast(DoubleType()).alias("value"),
        F.col("j.unit").alias("unit"),
        F.col("j.obs_status").alias("obs_status"),
        F.col("j.decimal").alias("decimal"),
        "ingestion_ts"
    )
    is_valid_iso3 = F.udf(lambda x: bool(valid_country_iso3(x)), BooleanType())
    is_valid_year = F.udf(lambda x: bool(valid_year(x)), BooleanType())
    clean = flat.where(is_valid_iso3(F.col("country_iso3")) & is_valid_year(F.col("year_str"))) \                .withColumn("year", F.col("year_str").cast(IntegerType())) \                .drop("year_str") \                .dropDuplicates(["indicator_id","country_iso3","year"])
    spark.sql(f"""
      CREATE TABLE IF NOT EXISTS {TABLE_SILVER} (
        indicator_id STRING,
        indicator_code STRING,
        indicator_name STRING,
        country_code2 STRING,
        country_name STRING,
        country_iso3 STRING,
        year INT,
        value DOUBLE,
        unit STRING,
        obs_status STRING,
        decimal INT,
        ingestion_ts TIMESTAMP
      ) USING DELTA
    """)
    clean.write.mode("overwrite").saveAsTable(TABLE_SILVER)
    print(f"[SILVER] Filas finales: {spark.table(TABLE_SILVER).count()}")

if __name__ == "__main__":
    main()
