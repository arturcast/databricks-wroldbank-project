# Terraform para Databricks (serverless + dashboard)

## Variables de entorno en CI
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`

## Variables TF (recomendadas)
- `TF_VAR_repo_url`
- `TF_VAR_repo_branch` (default `main`)
- `TF_VAR_sql_warehouse_name` (default `Starter Warehouse`)
- `TF_VAR_cron_time_bogota` (default `02:00`)

## Comandos locales
```bash
terraform init
terraform plan -var="repo_url=..." -var="repo_branch=main"
terraform apply -auto-approve -var="repo_url=..." -var="repo_branch=main"
```
