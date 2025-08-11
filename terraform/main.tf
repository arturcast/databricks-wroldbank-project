terraform {
  required_version = ">= 1.3.0"
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "1.44.0"
    }
  }
}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

locals {
  indicators_csv = join(",", var.indicators)

  # var.cron_time_bogota viene en formato "HH:MM", ej: "02:00"
  cron_hour   = tonumber(element(split(":", var.cron_time_bogota), 0))
  cron_minute = tonumber(element(split(":", var.cron_time_bogota), 1))

  # Quartz cron expression: sec min hour day-of-month month day-of-week ?
  quartz_expr = "0 ${local.cron_minute} ${local.cron_hour} * * ?"
}

resource "databricks_job" "worldbank" {
  name = "worldbank-medallion-serverless"

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

  # Declaración de environment serverless
  environments {
    environment_key = "srvless"
    spec = jsonencode({
      client              = "serverless"
      environment_version = "3"
    })
  }

  task {
    task_key        = "bronze_ingestion"
    environment_key = "srvless"

    spark_python_task {
      source      = "GIT"
      python_file = "src/jobs/01_ingestion_bronze.py"
      parameters  = [
        "--start-year", tostring(var.start_year),
        "--end-year", tostring(var.end_year),
        "--indicators", local.indicators_csv
      ]
    }
  }

  task {
    task_key        = "silver_transform"
    depends_on {
      task_key = "bronze_ingestion"
    }
    environment_key = "srvless"

    spark_python_task {
      source      = "GIT"
      python_file = "src/jobs/02_transform_silver.py"
    }
  }

  task {
    task_key        = "gold_aggregate"
    depends_on {
      task_key = "silver_transform"
    }
    environment_key = "srvless"

    spark_python_task {
      source      = "GIT"
      python_file = "src/jobs/03_aggregate_gold.py"
    }
  }
}

output "job_id" {
  description = "ID del job creado"
  value       = databricks_job.worldbank.id
}
