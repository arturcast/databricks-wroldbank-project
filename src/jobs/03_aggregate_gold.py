from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from src.common.config import TABLE_SILVER, TABLE_GOLD_METRICS, TABLE_GOLD_KPIS, CATALOG, SCHEMA
from src.common.utils import compute_yoy_growth

def main():
    spark = SparkSession.builder.appName("wb-gold-aggregate").getOrCreate()
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {CATALOG}.{SCHEMA}")
    df = spark.table(TABLE_SILVER)

    # Pivot indicadores a columnas
    pivot = (
        df.groupBy("country_iso3","country_name","year")
          .pivot("indicator_id")
          .agg(F.first("value", ignorenulls=True))
    )

    # Renombrar columnas relevantes
    mapping = {
        "SP.POP.TOTL": "population_total",
        "NY.GDP.MKTP.CD": "gdp_current_usd",
        "NY.GDP.PCAP.CD": "gdp_per_capita_ind",
        "SP.POP.GROW": "population_growth_pct_ind",
        "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct_ind",
    }
    for k, v in mapping.items():
        if k in pivot.columns:
            pivot = pivot.withColumnRenamed(k, v)

    # PIB per cápita: preferir indicador; fallback cálculo
    pivot = pivot.withColumn(
        "gdp_per_capita",
        F.when(F.col("gdp_per_capita_ind").isNotNull(), F.col("gdp_per_capita_ind")) \         .when((F.col("gdp_current_usd").isNotNull()) & (F.col("population_total") > 0),
               F.col("gdp_current_usd") / F.col("population_total")) \         .otherwise(F.lit(None))
    )

    # Crecimientos interanuales calculados (fallback)
    w = Window.partitionBy("country_iso3").orderBy("year")
    lag_pop = F.lag("population_total").over(w)
    lag_gdp = F.lag("gdp_current_usd").over(w)
    from pyspark.sql.types import DoubleType
    growth_udf = F.udf(compute_yoy_growth, DoubleType())
    pivot = (pivot
        .withColumn("population_yoy_growth_calc", growth_udf(F.col("population_total"), lag_pop))
        .withColumn("gdp_yoy_growth_calc", growth_udf(F.col("gdp_current_usd"), lag_gdp))
    )

    # Unificar crecimiento: preferir indicadores (%) -> convertir a proporción
    pivot = (pivot
        .withColumn("population_yoy_growth",
            F.when(F.col("population_growth_pct_ind").isNotNull(), F.col("population_growth_pct_ind")/100.0)
             .otherwise(F.col("population_yoy_growth_calc")))
        .withColumn("gdp_yoy_growth",
            F.when(F.col("gdp_growth_pct_ind").isNotNull(), F.col("gdp_growth_pct_ind")/100.0)
             .otherwise(F.col("gdp_yoy_growth_calc")))
    )

    metrics = pivot

    # Guardar GOLD
    metrics.write.mode("overwrite").saveAsTable(TABLE_GOLD_METRICS)

    # KPIs del último año por país
    last_year = metrics.groupBy("country_iso3").agg(F.max("year").alias("max_year"))
    latest = (metrics.alias("m")
              .join(last_year.alias("ly"),
                    (F.col("m.country_iso3") == F.col("ly.country_iso3")) & (F.col("m.year") == F.col("ly.max_year")),
                    "inner")
              .select("m.*"))

    latest.write.mode("overwrite").saveAsTable(TABLE_GOLD_KPIS)

    print(f"[GOLD] Metrics rows: {metrics.count()}, Latest rows: {latest.count()}")

if __name__ == "__main__":
    main()
