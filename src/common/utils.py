import json
from time import sleep
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

def _http_get_json(url: str, ua: str = "wb-databricks-portfolio/1.0", retry=3, backoff=1.5):
    last_err = None
    for attempt in range(retry):
        try:
            req = Request(url, headers={"User-Agent": ua})
            with urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
            return json.loads(raw)
        except (HTTPError, URLError) as e:
            last_err = e
            sleep(backoff ** (attempt + 1))
    raise last_err

def fetch_worldbank_indicator(indicator: str, start_year: int, end_year: int, per_page: int = 20000):
    params = {
        "date": f"{start_year}:{end_year}",
        "format": "json",
        "per_page": per_page
    }
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?{urlencode(params)}"
    data = _http_get_json(url)
    if not isinstance(data, list) or len(data) < 2:
        return []
    meta, observations = data[0], data[1]
    total_pages = meta.get("pages", 1) if isinstance(meta, dict) else 1
    results = list(observations or [])
    for page in range(2, total_pages + 1):
        paged_url = url + f"&page={page}"
        page_json = _http_get_json(paged_url)
        if isinstance(page_json, list) and len(page_json) >= 2:
            results.extend(page_json[1] or [])
    return results

def compute_yoy_growth(value, prev):
    if prev in (None, 0) or value is None:
        return None
    try:
        return (value - prev) / prev
    except ZeroDivisionError:
        return None

def safe_float(x):
    try:
        return float(x) if x is not None else None
    except Exception:
        return None
