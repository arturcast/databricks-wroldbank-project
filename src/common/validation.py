def valid_country_iso3(code: str) -> bool:
    return isinstance(code, str) and len(code) == 3 and code.isalpha()

def valid_year(year_str: str) -> bool:
    return isinstance(year_str, str) and year_str.isdigit()

def valid_value(v) -> bool:
    return v is None or isinstance(v, (int, float))

def is_valid_observation(rec: dict) -> bool:
    try:
        return (
            valid_country_iso3(rec.get("countryiso3code", "")) and
            valid_year(rec.get("date", "")) and
            valid_value(rec.get("value", None))
        )
    except Exception:
        return False
