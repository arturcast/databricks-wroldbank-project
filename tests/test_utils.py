from src.common.utils import compute_yoy_growth

def test_growth_basic():
    assert compute_yoy_growth(110, 100) == 0.1
    assert compute_yoy_growth(100, 100) == 0.0
    assert compute_yoy_growth(None, 100) is None
    assert compute_yoy_growth(100, None) is None
    assert compute_yoy_growth(100, 0) is None
