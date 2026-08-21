import hashlib
import time

import pytest


@pytest.fixture(autouse=True)
def _realistic_duration(request):
    # Deterministic, per-test duration (0.05-0.35s) derived from the test's
    # node id -- kept fixed from build #1 onward so the duration curve is
    # genuine and never bimodal (unlike the corrupted `tejas` history).
    digest = hashlib.sha256(request.node.nodeid.encode()).hexdigest()
    delay = 0.05 + (int(digest[:4], 16) % 300) / 1000
    time.sleep(delay)
