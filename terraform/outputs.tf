output "job_id" {
  description = "ID del job creado"
  value       = databricks_job.worldbank.id
}
output "dashboard_id" {
  description = "ID del dashboard SQL creado"
  value       = databricks_sql_dashboard.wb_dashboard.id
}
