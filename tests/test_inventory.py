import pytest
from app.inventory import is_in_stock, reserve_stock, low_stock_warning


@pytest.mark.critical
def test_reserve_stock_reduces_quantity():
    assert reserve_stock(10, 3) == 7


@pytest.mark.critical
def test_reserve_stock_rejects_overdraft():
    with pytest.raises(ValueError):
        reserve_stock(5, 10)


def test_is_in_stock_true_when_positive():
    assert is_in_stock(1) is True


def test_is_in_stock_false_when_zero():
    assert is_in_stock(0) is False


def test_low_stock_warning_triggers_below_threshold():
    assert low_stock_warning(3) is True


def test_low_stock_warning_false_when_ample():
    assert low_stock_warning(50) is False
