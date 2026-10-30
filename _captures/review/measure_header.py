"""Header measurement only: band height + how much of the header the brand fills.

Header band = the run of "glass" rows at the top (the header fill differs from the
page below it). Wordmark ink is measured strictly between the two action slots so
the cart glyph cannot contaminate the box.
"""

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


def load(path):
    im = Image.open(path).convert("RGB")
    if im.width != W:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    return np.asarray(im).astype(int)


def band_bottom(img, maxy=140):
    """Last row of the header: where the top strip stops matching its own colour."""
    strip = img[:maxy, 2:12].mean(axis=(1, 2))
    head = strip[2:12].mean()
    bottom = 0
    for y in range(2, maxy):
        if abs(strip[y] - head) < 3.0:
            bottom = y
        elif y - bottom > 6:
            break
    return bottom + 1


def ink_box(img, y0, y1, x0=62, x1=328):
    band = img[y0:y1, x0:x1]
    r, g, b = band[:, :, 0], band[:, :, 1], band[:, :, 2]
    mask = (r > 140) & (g > 30) & (g < 165) & (b < 120)
    ys, xs = np.where(mask)
    if len(xs) < 40:
        return None
    return x0 + int(xs.min()), x0 + int(xs.max()), y0 + int(ys.min()), y0 + int(ys.max())


ROWS = [
    ("stitch home", os.path.join(STITCH, "unified_home_dashboard", "screen.png")),
    ("bmj home dark", os.path.join(AFTER, "01_home.png")),
    ("bmj home light", os.path.join(AFTER, "01_home_light.png")),
    ("stitch pdp", os.path.join(STITCH, "juice_detail_selection", "screen.png")),
    ("bmj pdp light", os.path.join(AFTER, "02_pdp_light.png")),
    ("stitch cart", os.path.join(STITCH, "shopping_cart_savings_summary", "screen.png")),
    ("bmj cart light", os.path.join(AFTER, "03_cart_light.png")),
    ("stitch subs", os.path.join(STITCH, "subscription_management_portal", "screen.png")),
    ("bmj subs light", os.path.join(AFTER, "04_subscription_light.png")),
]

print(f"{'screen':<16} {'band':>5} {'ink w':>6} {'ink h':>6}  ink box")
for label, path in ROWS:
    img = load(path)
    bottom = band_bottom(img)
    box = ink_box(img, 0, bottom + 2)
    w = box[1] - box[0] + 1 if box else 0
    h = box[3] - box[2] + 1 if box else 0
    print(f"{label:<16} {bottom:5d} {w:6d} {h:6d}  {box}")
