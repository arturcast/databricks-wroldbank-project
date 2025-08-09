terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.84.0"
    }
  }
}

provider "databricks" {}

locals {
  indicators_csv = join(",", var.indicators)
  cron_hour      = tonumber(split(var.cron_time_bogota, ":")[0])
  cron_minute    = tonumber(split(var.cron_time_bogota, ":")[1])
  # Quartz: sec min hour day-of-month month day-of-week ? for daily: 0 MM HH * * ?
  quartz_expr    = "0 ${local.cron_minute} ${local.cron_hour} * * ?"
}

# --------------------
# JOB con schedule diario
# --------------------
resource "databricks_job" "worldbank" {
  name                 = var.job_name
  max_concurrent_runs  = 1

  git_source {
    url      = var.repo_url
    provider = "gitHub"
    branch   = var.repo_branch
  }

  schedule {
    quartz_cron_expression = local.quartz_expr
    timezone_id            = "America/Bogota"
    pause_status           = "UNPAUSED"
  }

  task {
    task_key = "bronze_ingestion"
    spark_python_task {
      source      = "GIT"
      python_file = "src/jobs/01_ingestion_bronze.py"
      parameters  = ["--start-year", tostring(var.start_year), "--end-year", tostring(var.end_year), "--indicators", local.indicators_csv]
    }
  }

  task {
    task_key = "silver_transform"
    depends_on { task_key = "bronze_ingestion" }
    spark_python_task {
      source      = "GIT"
      python_file = "src/jobs/02_transform_silver.py"
    }
  }

  task {
    task_key = "gold_aggregate"
    depends_on { task_key = "silver_transform" }
    spark_python_task {
      source      = "GIT"
      python_file = "src/jobs/03_aggregate_gold.py"
    }
  }
}

# --------------------
# DASHBOARD (SQL)
# --------------------
data "databricks_sql_warehouse" "wh" {
  name = var.sql_warehouse_name
}

resource "databricks_sql_query" "kpi_latest" {
  name           = "WB - KPIs último año por país"
  data_source_id = data.databricks_sql_warehouse.wh.id
  query          = <<SQL
SELECT country_iso3, country_name, year,
       population_total, gdp_current_usd, gdp_per_capita,
       population_yoy_growth, gdp_yoy_growth
FROM ${var.job_name == "" ? "hive_metastore.worldbank_demo.gold_kpis_latest" : "hive_metastore.worldbank_demo.gold_kpis_latest"}
ORDER BY gdp_current_usd DESC
SQL
}

resource "databricks_sql_query" "ts_population" {
  name           = "WB - Serie Población"
  data_source_id = data.databricks_sql_warehouse.wh.id
  query          = <<SQL
SELECT country_iso3, country_name, year, population_total
FROM hive_metastore.worldbank_demo.gold_country_year_metrics
WHERE population_total IS NOT NULL
ORDER BY country_iso3, year
SQL
}

resource "databricks_sql_query" "ts_gdp" {
  name           = "WB - Serie PIB USD"
  data_source_id = data.databricks_sql_warehouse.wh.id
  query          = <<SQL
SELECT country_iso3, country_name, year, gdp_current_usd
FROM hive_metastore.worldbank_demo.gold_country_year_metrics
WHERE gdp_current_usd IS NOT NULL
ORDER BY country_iso3, year
SQL
}

resource "databricks_sql_query" "top_gdp_pc" {
  name           = "WB - Top 10 PIB per cápita (último año)"
  data_source_id = data.databricks_sql_warehouse.wh.id
  query          = <<SQL
WITH last_year AS (
  SELECT country_iso3, MAX(year) AS max_year
  FROM hive_metastore.worldbank_demo.gold_country_year_metrics
  GROUP BY country_iso3
)
SELECT m.country_iso3, m.country_name, m.year, m.gdp_per_capita
FROM hive_metastore.worldbank_demo.gold_country_year_metrics m
JOIN last_year ly ON m.country_iso3 = ly.country_iso3 AND m.year = ly.max_year
WHERE m.gdp_per_capita IS NOT NULL
ORDER BY m.gdp_per_capita DESC
LIMIT 10
SQL
}

resource "databricks_sql_dashboard" "wb_dashboard" {
  name = "World Bank KPIs (Lakeview)"
}

resource "databricks_sql_widget" "w_kpi_latest" {
  dashboard_id = databricks_sql_dashboard.wb_dashboard.id
  text         = "KPIs último año por país"
  visualization_options = jsonencode({
    type = "table"
  })
  query_id = databricks_sql_query.kpi_latest.id
  position = jsonencode({x=0,y=0,w=24,h=10})
}

resource "databricks_sql_widget" "w_ts_population" {
  dashboard_id = databricks_sql_dashboard.wb_dashboard.id
  text         = "Población (serie)"
  visualization_options = jsonencode({
    type = "lines"
  })
  query_id = databricks_sql_query.ts_population.id
  position = jsonencode({x=0,y=10,w=12,h=12})
}

resource "databricks_sql_widget" "w_ts_gdp" {
  dashboard_id = databricks_sql_dashboard.wb_dashboard.id
  text         = "PIB USD (serie)"
  visualization_options = jsonencode({
    type = "lines"
  })
  query_id = databricks_sql_query.ts_gdp.id
  position = jsonencode({x=12,y=10,w=12,h=12})
}

resource "databricks_sql_widget" "w_top_gdp_pc" {
  dashboard_id = databricks_sql_dashboard.wb_dashboard.id
  text         = "Top 10 PIB per cápita (último año)"
  visualization_options = jsonencode({
    type = "bars"
  })
  query_id = databricks_sql_query.top_gdp_pc.id
  position = jsonencode({x=0,y=22,w=24,h=12})
}
