variable "repo_url" {
  description = "URL del repo Git"
  type        = string
}
variable "repo_branch" {
  description = "Rama del repo"
  type        = string
  default     = "main"
}
variable "job_name" {
  description = "Nombre del job de Databricks"
  type        = string
  default     = "worldbank-medallion-serverless"
}
variable "start_year" {
  type        = number
  default     = 1995
}
variable "end_year" {
  type        = number
  default     = 2024
}
variable "indicators" {
  description = "Lista de indicadores WB"
  type        = list(string)
  default     = ["SP.POP.TOTL","NY.GDP.MKTP.CD","NY.GDP.PCAP.CD","SP.POP.GROW","NY.GDP.MKTP.KD.ZG"]
}
variable "sql_warehouse_name" {
  description = "Nombre del SQL Warehouse para el dashboard"
  type        = string
  default     = "Starter Warehouse"
}
variable "cron_time_bogota" {
  description = "Hora de ejecución diaria (America/Bogota) en formato HH:MM (24h)"
  type        = string
  default     = "02:00"
}
