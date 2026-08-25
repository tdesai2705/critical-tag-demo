"""Toggle a module's deliberate boundary bug on/off for confidence-model
training history. Real, deterministic, single-line source change -- not
synthetic flakiness -- so Smart Tests has a genuine failure to correlate
with a genuine git diff in that module's directory.

Usage: python3 scripts/toggle_bug.py <module> <safe|buggy>
"""
import sys

SAFE_LINE = "    if value > LIMIT:  # BUG-TOGGLE-LINE: safe='>' buggy='>='\n"
BUGGY_LINE = "    if value >= LIMIT:  # BUG-TOGGLE-LINE: safe='>' buggy='>='\n"


def main():
    module, mode = sys.argv[1], sys.argv[2]
    if mode not in ("safe", "buggy"):
        raise SystemExit(f"mode must be 'safe' or 'buggy', got {mode!r}")

    path = f"app/{module}/__init__.py"
    with open(path) as f:
        lines = f.readlines()

    target = BUGGY_LINE if mode == "buggy" else SAFE_LINE
    other = SAFE_LINE if mode == "buggy" else BUGGY_LINE

    changed = False
    for i, line in enumerate(lines):
        if line in (SAFE_LINE, BUGGY_LINE):
            lines[i] = target
            changed = True
            break

    if not changed:
        raise SystemExit(f"BUG-TOGGLE-LINE not found in {path}")

    with open(path, "w") as f:
        f.writelines(lines)

    print(f"{module}: set to {mode}")


if __name__ == "__main__":
    main()
