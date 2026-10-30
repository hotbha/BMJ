"""Scan (and optionally repair) mojibake in BMJ Dart sources.

Several files were saved after a UTF-8 -> cp1252 -> UTF-8 round trip, so real
user-visible strings turned into ``\u00c3\u00a2\u00c2\u00b7`` style garbage
(for example the PDP CTA rendered "Add to cart \u00c3\u00a2\u00c2\u00b7 \u00e2\u201a\u00b9150"
instead of "Add to cart \u00b7 \u20b9150"). That is a product bug, not a cosmetic one,
and it is exactly what four `product_detail_screen_test` assertions were
catching.

Usage:
    python _fix_mojibake.py            # report only
    python _fix_mojibake.py --apply    # rewrite the affected files
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "lush"
TARGET_DIRS = (ROOT / "lib", ROOT / "test", ROOT / "integration_test")

# Corrupted sequence -> character it should be. Sorted longest first at runtime
# so a double-encoded sequence is repaired before its shorter prefix.
REPAIRS: list[tuple[str, str]] = [
    # Double-encoded (UTF-8 -> cp1252 -> UTF-8, twice).
    ("\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u009d", "\u2014"),
    ("\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u0153", "\u2013"),
    ("\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u201e\u00a2", "\u2019"),
    ("\u00c3\u00a2\u00e2\u201a\u00ac\u00c5\u201c", "\u201c"),
    ("\u00c3\u00a2\u00e2\u201a\u00ac\u009d", "\u201d"),
    ("\u00c3\u00a2\u00e2\u201a\u00ac\u00a6", "\u2026"),
    ("\u00c3\u00a2\u201a\u00b9", "\u20b9"),
    ("\u00c3\u00a2\u00c2\u00b7", "\u00b7"),
    ("\u00c3\u00a2\u2020\u2019", "\u2192"),
    # Single-encoded (UTF-8 read as cp1252, saved back as UTF-8).
    ("\u00e2\u20ac\u201d", "\u2014"),   # em dash
    ("\u00e2\u20ac\u2013", "\u2013"),   # en dash
    ("\u00e2\u20ac\u2122", "\u2019"),   # right single quote
    ("\u00e2\u20ac\u0153", "\u201c"),   # left double quote
    ("\u00e2\u20ac\u009d", "\u201d"),   # right double quote
    ("\u00e2\u20ac\u00a6", "\u2026"),   # ellipsis
    ("\u00e2\u201a\u00b9", "\u20b9"),   # rupee sign
    ("\u00e2\u2020\u2019", "\u2192"),   # arrow
    ("\u00c2\u00b7", "\u00b7"),         # middle dot
    ("\u00c2\u00a0", " "),             # no-break space
    ("\u00c2\u00b0", "\u00b0"),         # degree
    ("\u00c3\u2014", "\u00d7"),         # multiply
]

MARKERS = tuple({seq[:2] for seq, _ in REPAIRS})


def iter_dart_files():
    for base in TARGET_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.dart"):
            yield path


def main() -> int:
    apply = "--apply" in sys.argv[1:]
    repairs = sorted(REPAIRS, key=lambda pair: len(pair[0]), reverse=True)
    touched = 0
    for path in iter_dart_files():
        with path.open("r", encoding="utf-8", newline="") as handle:
            text = handle.read()
        if not any(marker in text for marker in MARKERS):
            continue
        repaired = text
        for bad, good in repairs:
            repaired = repaired.replace(bad, good)
        hits = sum(text.count(marker) for marker in MARKERS)
        rel = path.relative_to(ROOT)
        print(f"{rel}: {hits} suspicious sequence(s)")
        if apply and repaired != text:
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(repaired)
            touched += 1
    print(f"\n{('repaired ' + str(touched)) if apply else 'report-only'} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
