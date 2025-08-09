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