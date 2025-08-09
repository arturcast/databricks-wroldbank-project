from src.common.validation import valid_country_iso3, valid_year, valid_value, is_valid_observation

def test_iso3():
    assert valid_country_iso3("COL")
    assert not valid_country_iso3("CO")
    assert not valid_country_iso3("123")

def test_year():
    assert valid_year("2022")
    assert not valid_year("20A2")

def test_value():
    assert valid_value(10.0)
    assert valid_value(None)
    assert not valid_value("foo")

def test_observation():
    rec = {"countryiso3code":"COL","date":"2020","value":500}
    assert is_valid_observation(rec)
    rec2 = {"countryiso3code":"C","date":"2020","value":500}
    assert not is_valid_observation(rec2)
