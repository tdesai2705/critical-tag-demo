"""warranty claim value ceiling module. LIMIT is a real boundary business rule --
the `> LIMIT` check below is the deliberate bug-toggle point used to build
genuine (not synthetic) pass/fail history for Smart Tests confidence-model
training: flipping `>` to `>=` is a real off-by-one boundary bug that makes
`test_process_at_exact_limit_succeeds` fail deterministically.

Unlike the other 6 modules, this module was added AFTER the original 24-commit
training loop and has NEVER been toggled to buggy before this decisive test --
used specifically to check whether the confidence model's nudge behavior
differs for a genuinely novel failure vs. one it has already observed
(pricing was toggled buggy twice during training; this module never has).
"""

LIMIT = 800
RATE = 0.65


def process(value):
    if value < 0:
        raise ValueError("value must be non-negative")
    if value >= LIMIT:  # BUG-TOGGLE-LINE: safe='>' buggy='>='
        raise ValueError(f"value must not exceed {LIMIT}")
    return round(value * RATE, 2)
