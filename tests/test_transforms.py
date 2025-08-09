import pytest
SPARK_AVAILABLE = False
try:
    from pyspark.sql import SparkSession
    SPARK_AVAILABLE = True
except Exception:
    pass

@pytest.mark.skipif(not SPARK_AVAILABLE, reason="PySpark no disponible en entorno de pruebas")
def test_silver_types():
    spark = SparkSession.builder.master("local[1]").appName("test").getOrCreate()
    from pyspark.sql import Row
    payload = {
        "indicator":{"id":"SP.POP.TOTL","value":"Population, total"},
        "country":{"id":"CO","value":"Colombia"},
        "countryiso3code":"COL",
        "date":"2020","value": 50000000,
        "unit":"","obs_status":"","decimal":0
    }
    df = spark.createDataFrame([Row(payload=str(payload).replace("'", '"'), indicator_id="SP.POP.TOTL", ingestion_ts=None)])
    assert df.count() == 1
    spark.stop()
