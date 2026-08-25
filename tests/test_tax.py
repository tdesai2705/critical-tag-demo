import pytest

from app.tax import process, LIMIT, RATE


def _expected(value):
    return round(value * RATE, 2)


PARAM_VALUES = sorted({
    0, 1, 2, 3, 5,
    max(1, LIMIT // 20),
    max(1, LIMIT // 10),
    LIMIT // 4,
    LIMIT // 3,
    LIMIT // 2,
    (LIMIT * 2) // 3,
    (LIMIT * 3) // 4,
    max(0, LIMIT - 5),
    max(0, LIMIT - 2),
})


@pytest.mark.parametrize("value", PARAM_VALUES)
def test_process_normal_values(value):
    assert process(value) == _expected(value)


def test_process_negative_raises():
    with pytest.raises(ValueError):
        process(-1)


def test_process_over_limit_raises():
    with pytest.raises(ValueError):
        process(LIMIT + 1)


def test_process_zero_is_zero():
    assert process(0) == 0.0


def test_process_returns_float():
    assert isinstance(process(10 if LIMIT > 10 else 0), float)


def test_process_rounds_to_two_decimals():
    result = process(min(7, LIMIT))
    assert result == round(result, 2)


def test_process_is_monotonic_for_small_step():
    low = min(3, LIMIT)
    high = min(4, LIMIT)
    if low != high:
        assert process(high) >= process(low)


@pytest.mark.critical
def test_process_at_exact_limit_succeeds():
    # boundary case -- this is the one the bug-toggle line breaks
    assert process(LIMIT) == _expected(LIMIT)


@pytest.mark.critical
def test_process_core_business_rule():
    # core invariant for this module -- must never silently break
    midpoint = LIMIT // 2
    assert process(midpoint) == _expected(midpoint)
