"""Measure the six Tier-1 moves on the freshly regenerated renders."""

import os
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STITCH = os.path.join(
    ROOT, "Stitch", "stitch_bookmyjuice_flutter_bloc_ui",
    "stitch_bookmyjuice_flutter_bloc_ui",
)
AFTER = os.path.join(ROOT, "_captures", "after")
W = 390


def load(path, gray=False):
    im = Image.open(path).convert("L" if gray else "RGB")
    if im.width != W:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    return np.asarray(im).astype(int)


def text_runs(img, y0, y1, x0=40, x1=350, dark=115, min_px=4):
    """Vertical runs of dark ink = text lines, with their ink heights."""
    band = img[y0:y1, x0:x1]
    rows = (band < dark).sum(axis=1)
    out, start = [], None
    for i, v in enumerate(rows):
        if v >= min_px and start is None:
            start = i
        elif v < min_px and start is not None:
            if i - start >= 4:
                out.append((y0 + start, y0 + i - 1, i - start))
            start = None
    return out


def orange_mass(img, y0, y1, x0=0, x1=W):
    band = img[y0:y1, x0:x1]
    r, g, b = band[:, :, 0], band[:, :, 1], band[:, :, 2]
    m = (r > 215) & (g > 85) & (g < 185) & (b < 110)
    return int(m.sum())


print("=== 1. PDP name vs price (ink heights inside the title card) ===")
for label, path in (
    ("stitch pdp", os.path.join(STITCH, "juice_detail_selection", "screen.png")),
    ("bmj pdp light", os.path.join(AFTER, "02_pdp_light.png")),
):
    img = load(path, gray=True)
    for y0, y1 in ((560, 700), (540, 700), (520, 700)):
        runs = text_runs(img, y0, y1, 40, 350, dark=120, min_px=6)
        if len(runs) >= 2:
            print(f"{label:<15} y{y0}-{y1}: line heights {[r[2] for r in runs[:4]]}")
            break

print()
print("=== 2. primary numeric values ===")
img = load(os.path.join(AFTER, "01_home_light.png"), gray=True)
print("home stat strip ink:", [r[2] for r in text_runs(img, 400, 520, 30, 360, dark=120, min_px=6)][:6])
img = load(os.path.join(AFTER, "03_cart_light.png"), gray=True)
print("cart row ink:", [r[2] for r in text_runs(img, 100, 260, 150, 380, dark=120, min_px=6)][:8])

print()
print("=== 3. nav active state (solid-accent pixels in the nav band) ===")
for label, path, band in (
    ("stitch home", os.path.join(STITCH, "unified_home_dashboard", "screen.png"), (800, 884)),
    ("bmj home light", os.path.join(AFTER, "01_home_light.png"), (760, 844)),
    ("stitch cart", os.path.join(STITCH, "shopping_cart_savings_summary", "screen.png"), (865, 926)),
    ("bmj cart light", os.path.join(AFTER, "03_cart_light.png"), (760, 844)),
):
    img = load(path)
    print(f"{label:<15} accent px = {orange_mass(img, band[0], band[1])}")

print()
print("=== 4. purchase option payoff (accent mass in the options block) ===")
img = load(os.path.join(AFTER, "02_pdp_light.png"))
print("bmj pdp options band accent px =", orange_mass(img, 780, 844))

print()
print("=== 5. subscription delivery/billing value ink height ===")
for label, path, band in (
    ("stitch subs", os.path.join(STITCH, "subscription_management_portal", "screen.png"), (330, 500)),
    ("bmj subs light", os.path.join(AFTER, "04_subscription_light.png"), (330, 470)),
):
    img = load(path, gray=True)
    print(f"{label:<15} lines {[r[2] for r in text_runs(img, band[0], band[1], 30, 380, dark=125, min_px=6)][:8]}")

print()
print("=== 6. checkout CTA bloom (halo rows under the button) ===")
for label, path in (
    ("stitch cart", os.path.join(STITCH, "shopping_cart_savings_summary", "screen.png")),
    ("bmj cart light", os.path.join(AFTER, "03_cart_light.png")),
):
    img = load(path)
    green = img[:, :, 1]
    red = img[:, :, 0]
    halo_rows = []
    for y in range(700, 844):
        row = img[y, 20:370]
        warm = ((row[:, 0] > 235) & (row[:, 1] > 150) & (row[:, 1] < 245)).sum()
        if warm > 40:
            halo_rows.append(y)
    print(f"{label:<15} warm halo rows y={halo_rows[0] if halo_rows else None}..{halo_rows[-1] if halo_rows else None}")
