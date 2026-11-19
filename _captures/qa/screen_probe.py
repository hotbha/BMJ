"""Characterise a device screenshot without a viewer: is it a real UI or a blank screen?"""
import sys

import numpy as np
from PIL import Image

path = sys.argv[1]
im = Image.open(path).convert("RGB")
a = np.asarray(im).astype(float)
h, w, _ = a.shape
lum = a.mean(axis=2)

print(f"file      : {path}")
print(f"size      : {w}x{h}")
print(f"mean lum  : {lum.mean():.1f}")
print(f"std lum   : {lum.std():.1f}   (near 0 => flat/blank)")
print(f"dark share: {(lum < 40).mean() * 100:.1f}%")

bands = 10
print("horizontal bands (mean luminance):")
for i in range(bands):
    lo, hi = int(i * h / bands), int((i + 1) * h / bands)
    print(f"  band {i} ({lo:>4}-{hi:>4}): {lum[lo:hi].mean():6.1f}")

# colour diversity: a blank screen has very few unique quantised colours
q = (a // 32).astype(np.int32)
uniq = len(np.unique(q[:, :, 0] * 100 + q[:, :, 1] * 10 + q[:, :, 2]))
print(f"coarse colour buckets: {uniq}  (>20 suggests real content)")
