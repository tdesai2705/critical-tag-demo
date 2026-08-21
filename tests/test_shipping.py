import pytest
from app.shipping import estimate_delivery_days, calculate_shipping_cost


@pytest.mark.critical
def test_estimate_delivery_days_standard():
    assert estimate_delivery_days(1000) == 2


@pytest.mark.critical
def test_calculate_shipping_cost_standard():
    assert calculate_shipping_cost(10) == 7.5


def test_estimate_delivery_days_express_is_faster():
    assert estimate_delivery_days(1000, express=True) < estimate_delivery_days(1000)


def test_calculate_shipping_cost_express_costs_more():
    assert calculate_shipping_cost(10, express=True) > calculate_shipping_cost(10)


def test_estimate_delivery_days_minimum_is_one():
    assert estimate_delivery_days(10) == 1
