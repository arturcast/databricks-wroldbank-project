# IMPLEMENTACION.md — databricks-wroldbank-project

## Prerrequisitos
- Databricks Free Edition con **Serverless Jobs** habilitado.
- GitHub Actions habilitado en el repo.

## Secretos en GitHub (Settings → Secrets and variables → Actions)
- `DATABRICKS_HOST`: URL del workspace (https://xxx.cloud.databricks.com)
- `DATABRICKS_TOKEN`: Token con permisos para Jobs y SQL

## Variables recomendadas (Settings → Variables → Actions)
- `TF_VAR_repo_url`: URL del repo Git (https).
- `TF_VAR_repo_branch`: rama (default `main`).
- `TF_VAR_sql_warehouse_name`: nombre del **SQL Warehouse** (default `Starter Warehouse`).

## Despliegue
1. Ejecuta el workflow **databricks-pipeline** (manual o push a `main`).
2. Terraform creará:
   - **Job** con 3 tareas secuenciales y **cron diario 02:00 America/Bogota**.
   - **Databricks SQL Dashboard** (Lakeview clásico) enlazado a tu Warehouse.
3. El workflow también ejecutará el Job una vez (Run Now) tras crear la infra.


