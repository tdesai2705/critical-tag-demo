"""redeemable loyalty points module. LIMIT is a real boundary business rule --
the `> LIMIT` check below is the deliberate bug-toggle point used to build
genuine (not synthetic) pass/fail history for Smart Tests confidence-model
training: flipping `>` to `>=` is a real off-by-one boundary bug that makes
`test_process_at_exact_limit_succeeds` fail deterministically.
"""

LIMIT = 5000
RATE = 0.75


def process(value):
    if value < 0:
        raise ValueError("value must be non-negative")
    if value > LIMIT:  # BUG-TOGGLE-LINE: safe='>' buggy='>='
        raise ValueError(f"value must not exceed {LIMIT}")
    return round(value * RATE, 2)
