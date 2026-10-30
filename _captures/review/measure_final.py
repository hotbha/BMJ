"""Evidence for the final pass: status dot, card divider, title weight,
nutrition panels, name/price dominance."""

import os
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AFTER = os.path.join(ROOT, "_captures", "after")
W = 390


def load(path, gray=False):
    im = Image.open(path).convert("L" if gray else "RGB")
    if im.width != W:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    return np.asarray(im).astype(int)


def text_runs(img, y0, y1, x0, x1, dark=115, min_px=4):
    band = img[y0:y1, x0:x1]
    rows = (band < dark).sum(axis=1)
    out, start = [], None
    for i, v in enumerate(rows):
        if v >= min_px and start is None:
            start = i
        elif v < min_px and start is not None:
            if i - start >= 5:
                out.append((y0 + start, i - start))
            start = None
    return out


def runs(mask):
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(mask) - 1))
    return out


rgbs = load(os.path.join(AFTER, "04_subscription_light.png"))
grays = load(os.path.join(AFTER, "04_subscription_light.png"), gray=True)

print("=== SUBSCRIPTION ===")
# 1. status dot: saturated green pixels in the card header band
r, g, b = rgbs[:, :, 0], rgbs[:, :, 1], rgbs[:, :, 2]
green = (g > 150) & (r < 160) & (b < 170) & (g - r > 50) & (g - b > 40)
sub = green[230:300, 30:370]
ys, xs = np.where(sub)
if len(xs):
    print(f"status dot: {sub.sum()} px bbox x={xs.min()+30}..{xs.max()+30} "
          f"y={ys.min()+230}..{ys.max()+230}")
else:
    print("status dot: not found")

# 2. page title ink height (first text run in the title band)
title = text_runs(grays, 60, 120, 30, 370, dark=130, min_px=4)
print("title/subtitle ink heights:", [t[1] for t in title][:3])

# 3. inner hairline: every full-width mid-tone row inside the card body
card_top, card_bottom = 300, 560
lum = grays[card_top:card_bottom, 40:350]
rule_rows = [card_top + i for i, row in enumerate(lum)
             if ((row > 180) & (row < 250)).sum() >= 300]
print(f"full-width mid-tone rows inside card: {rule_rows[:6]} ... {rule_rows[-3:] if rule_rows else ''}")

print()
print("=== PDP ===")
pdp = load(os.path.join(AFTER, "02_pdp_light.png"), gray=True)
pdp_rgb = load(os.path.join(AFTER, "02_pdp_light.png"))
# name + price ink in the title card: widest ink band = the name
runs_t = text_runs(pdp, 470, 700, 40, 350, dark=130, min_px=6)
print("title-card ink runs (y, height):", runs_t[:6])

# nutrition panels: near-white card runs at several rows in the panels band
white = (np.abs(pdp_rgb - np.array([255, 255, 255])).max(axis=2) < 8)
for probe in (660, 680, 700, 720):
    cols = [c for c in runs(white[probe]) if c[1] - c[0] > 40]
    print(f"  row y={probe}: card runs={cols}")
