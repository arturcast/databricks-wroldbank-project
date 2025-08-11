import argparse
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from src.common.config import (
    DEFAULT_INDICATORS, START_YEAR, END_YEAR, SCHEMA, TABLE_BRONZE, CATALOG, WB_PER_PAGE
)
from src.common.utils import fetch_worldbank_indicator

def ensure_schema(spark):
    # Unity Catalog
    spark.sql(f"USE CATALOG {CATALOG}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
    spark.sql(f"USE {CATALOG}.{SCHEMA}")

def main(indicators, start_year, end_year):
    spark = SparkSession.builder.appName("wb-bronze-ingestion").getOrCreate()
    ensure_schema(spark)
    rows = []
    for ind in indicators:
        observations = fetch_worldbank_indicator(ind, start_year, end_year, per_page=WB_PER_PAGE)
        for obs in observations:
            rows.append({
                "payload": json.dumps(obs, ensure_ascii=False),
                "indicator_id": ind,
                "source": "worldbank",
            })
    if rows:
        df = spark.createDataFrame(rows)
    else:
        df = spark.createDataFrame([], schema="payload string, indicator_id string, source string")
    df = df.withColumn("ingestion_ts", current_timestamp())
    spark.sql(f"""
      CREATE TABLE IF NOT EXISTS {TABLE_BRONZE} (
        payload STRING,
        indicator_id STRING,
        source STRING,
        ingestion_ts TIMESTAMP
      ) USING DELTA
    """)
    df.select("payload","indicator_id","source","ingestion_ts").write.mode("append").saveAsTable(TABLE_BRONZE)
    print(f"[BRONZE] Registros totales: {spark.table(TABLE_BRONZE).count()}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--indicators", type=str, default=",".join(DEFAULT_INDICATORS))
    p.add_argument("--start-year", type=int, default=START_YEAR)
    p.add_argument("--end-year", type=int, default=END_YEAR)
    args = p.parse_args()
    indicators = [s.strip() for s in args.indicators.split(",") if s.strip()]
    main(indicators, args.start_year, args.end_year)
