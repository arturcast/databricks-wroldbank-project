import os
from datetime import datetime

DEFAULT_INDICATORS = os.getenv(
    "INDICATORS",
    "SP.POP.TOTL,NY.GDP.MKTP.CD,NY.GDP.PCAP.CD,SP.POP.GROW,NY.GDP.MKTP.KD.ZG"
).split(",")

CURRENT_YEAR = datetime.utcnow().year
START_YEAR = int(os.getenv("START_YEAR", CURRENT_YEAR - 30))
END_YEAR = int(os.getenv("END_YEAR", CURRENT_YEAR - 1))

CATALOG = os.getenv("CATALOG", "main")
SCHEMA = os.getenv("SCHEMA", "worldbank_demo")

TABLE_BRONZE = f"{CATALOG}.{SCHEMA}.bronze_observations"
TABLE_SILVER = f"{CATALOG}.{SCHEMA}.silver_observations"
TABLE_GOLD_METRICS = f"{CATALOG}.{SCHEMA}.gold_country_year_metrics"
TABLE_GOLD_KPIS = f"{CATALOG}.{SCHEMA}.gold_kpis_latest"

WB_BASE = "https://api.worldbank.org/v2"
WB_PER_PAGE = int(os.getenv("WB_PER_PAGE", "20000"))
