import pytest
from app.pricing import apply_discount, calculate_tax, total_with_tax


@pytest.mark.critical
def test_apply_discount_reduces_price_correctly():
    assert apply_discount(100, 20) == 80.0


@pytest.mark.critical
def test_apply_discount_rejects_out_of_range_percent():
    with pytest.raises(ValueError):
        apply_discount(100, 150)


def test_apply_discount_zero_percent_is_noop():
    assert apply_discount(50, 0) == 50.0


def test_calculate_tax_default_rate():
    assert calculate_tax(100) == 8.0


def test_total_with_tax_adds_correctly():
    assert total_with_tax(100) == 108.0
