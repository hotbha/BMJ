r"""Pricing-correctness audit for the launch surfaces.

Scans the four migrated screens, the shared BMJ component library and the
shared size sheet for fabricated money: hardcoded rupee literals, `?? 0`
price fallbacks and `.99` style placeholder amounts.

Usage:  python X:\BMJ\_captures\audit_pricing.py
Exit code 1 when a suspicious pattern is found.
"""

import re
import sys
from pathlib import Path

ROOT = Path(r"X:\BMJ\lush\lib")

FILES = [
    "views/screens/detail.dart",
    "views/screens/home_tab.dart",
    "views/screens/cart_screen.dart",
    "views/screens/subscription_management_screen.dart",
    "views/widgets/size_selection_sheet.dart",
    "widgets/bmj_amount_row.dart",
    "widgets/bmj_glass_card.dart",
    "widgets/bmj_glass_button.dart",
    "widgets/bmj_pill.dart",
    "widgets/bmj_stat_tile.dart",
    "utils/price_utils.dart",
]

# Fabricated money only. Alpha values such as 0.75 are legitimate.
PATTERNS = [
    ("hardcoded_rupee_literal", re.compile(r"(?<![\w.])Rs\.?\s*\d")),
    ("hardcoded_rupee_symbol", re.compile(r"\u20b9\s*\d")),
    ("placeholder_99", re.compile(r"(?<![\w.])\d+\.99\b")),
    ("null_price_to_zero", re.compile(r"price[^;\n]{0,40}\?\?\s*0(\.0+)?\b")),
    ("null_amount_to_zero", re.compile(r"(amount|total|subtotal)[^;\n]{0,30}\?\?\s*0(\.0+)?\b")),
]

ALLOW = re.compile(r"withValues\(alpha|alpha:|opacity")


def main() -> int:
    try:  # the console is cp1252 on some Windows shells; the report has ₹
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover - very old Python
        pass

    problems = 0
    for rel in FILES:
        path = ROOT / rel
        if not path.exists():
            print(f"MISSING  {rel}")
            problems += 1
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if ALLOW.search(line):
                continue
            for name, pattern in PATTERNS:
                if pattern.search(line):
                    print(f"{rel}:{lineno}: [{name}] {line.strip()}")
                    problems += 1

    print(f"\n{problems} suspicious line(s) in {len(FILES)} in-scope files")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
