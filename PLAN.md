# PLAN.md — databricks-wroldbank-project

## Objetivo
Construir un pipeline de Data Engineering en Databricks (Free Edition, serverless) que:
- Ingesta indicadores del Banco Mundial (población total, PIB en USD, PIB per cápita, crecimientos %).
- Estructura los datos con arquitectura Medallion.
- Publica métricas (KPIs) listas para consumo analítico.
- Se despliega vía Terraform y se ejecuta por GitHub Actions en secuencia.
- **Programación diaria** con cron en el Job de Databricks.

## Fases y tareas

### Fase 0 — Repo & CI/CD
- [ ] Crear repositorio GitHub público llamado **databricks-wroldbank-project**.
- [ ] Añadir workflow `.github/workflows/databricks_pipeline.yml`.
- [ ] Configurar secretos: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`.
- [ ] (Opcional) `TF_VAR_repo_url`, `TF_VAR_repo_branch`, `TF_VAR_sql_warehouse_name`.

### Fase 1 — Infraestructura (Terraform)
- [ ] Proveedor Databricks.
- [ ] `databricks_job` con 3 tareas `spark_python_task` (GIT source) y `max_concurrent_runs=1`.
- [ ] **Schedule diario** (02:00 America/Bogota).
- [ ] Dependencias entre tareas: Bronze → Silver → Gold (secuencial).
- [ ] Sin clúster: uso de serverless por defecto (Jobs).

### Fase 2 — Capa Bronze
- [ ] Ingestar REST API (World Bank) para indicadores:
  - `SP.POP.TOTL` (Población total)
  - `NY.GDP.MKTP.CD` (PIB USD actuales)
  - `NY.GDP.PCAP.CD` (PIB per cápita USD actuales)
  - `SP.POP.GROW` (Crecimiento poblacional anual, %)
  - `NY.GDP.MKTP.KD.ZG` (Crecimiento PIB anual, %)

### Fase 3 — Capa Silver
- [ ] Parsear/limpiar: tipificar, aplanar, validar, deduplicar.
- [ ] Tabla `silver_observations`.

### Fase 4 — Capa Gold
- [ ] Agregar métricas por país/año.
- [ ] KPIs: crecimiento poblacional anual, crecimiento PIB, PIB per cápita (preferencia indicador; fallback cálculo).
- [ ] Tablas `gold_country_year_metrics` y `gold_kpis_latest`.



### Fase 6 — Pruebas
- [ ] `pytest` sobre funciones puras y (opcional) transformaciones con Spark local.

### Fase 7 — Documentación
- [ ] `README.md`, `IMPLEMENTACION.md` y `LINKEDIN_POST.md` actualizados.
