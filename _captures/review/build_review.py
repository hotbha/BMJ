"""Build screenshot-first comparison sheets: Stitch | BMJ now | blend overlay.

No scoring, no token values - the output is only meant to be looked at.
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STITCH = os.path.join(
    ROOT,
    "Stitch",
    "stitch_bookmyjuice_flutter_bloc_ui",
    "stitch_bookmyjuice_flutter_bloc_ui",
)
OUT = os.path.dirname(os.path.abspath(__file__))
AFTER = os.path.join(ROOT, "_captures", "after")

W = 390  # comparison width (logical phone width)
GUTTER = 28
LABEL_H = 46

SCREENS = [
    ("01_home", "unified_home_dashboard", "01_home.png", "01_home_light.png"),
    ("02_pdp", "juice_detail_selection", "02_pdp.png", "02_pdp_light.png"),
    ("03_cart", "shopping_cart_savings_summary", "03_cart.png", "03_cart_light.png"),
    (
        "04_subscription",
        "subscription_management_portal",
        "04_subscription.png",
        "04_subscription_light.png",
    ),
]


def font(size):
    for name in ("arialbd.ttf", "arial.ttf", "segoeuib.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def norm(path):
    im = Image.open(path).convert("RGB")
    h = round(im.height * W / im.width)
    return im.resize((W, h), Image.LANCZOS)


def ruler(im):
    """Draw a 100 px horizontal grid so vertical alignment is readable."""
    out = im.copy()
    d = ImageDraw.Draw(out)
    for y in range(0, out.height, 100):
        d.line([(0, y), (out.width, y)], fill=(0, 160, 255), width=1)
        d.text((4, y + 2), str(y), font=font(11), fill=(0, 160, 255))
    return out


def labelled(im, text):
    out = Image.new("RGB", (im.width, im.height + LABEL_H), (18, 18, 20))
    out.paste(im, (0, LABEL_H))
    d = ImageDraw.Draw(out)
    d.text((8, 10), text, font=font(22), fill=(255, 255, 255))
    return out


for name, folder, dark_file, light_file in SCREENS:
    stitch = norm(os.path.join(STITCH, folder, "screen.png"))
    dark = norm(os.path.join(AFTER, dark_file))
    light = norm(os.path.join(AFTER, light_file))

    # 1. three panels: reference | our dark theme | our light theme
    panels = [
        labelled(ruler(stitch), "STITCH"),
        labelled(ruler(dark), "BMJ DARK"),
        labelled(ruler(light), "BMJ LIGHT"),
    ]
    h = max(p.height for p in panels)
    total_w = W * 3 + GUTTER * 2
    sheet = Image.new("RGB", (total_w, h), (10, 10, 12))
    x = 0
    for p in panels:
        sheet.paste(p, (x, 0))
        x += W + GUTTER
    d = ImageDraw.Draw(sheet)
    for gx in (W + GUTTER // 2, (W + GUTTER) * 2 - GUTTER // 2):
        d.line([(gx, 0), (gx, h)], fill=(120, 120, 130), width=2)
    sheet.save(os.path.join(OUT, f"{name}_side.png"))

    # 2. blend overlay against our dark theme (the reference's own material)
    hh = min(stitch.height, dark.height)
    over = Image.blend(stitch.crop((0, 0, W, hh)), dark.crop((0, 0, W, hh)), 0.5)
    d = ImageDraw.Draw(over)
    for y in range(0, hh, 100):
        d.line([(0, y), (W, y)], fill=(0, 160, 255), width=1)
        d.text((4, y + 2), str(y), font=font(11), fill=(0, 160, 255))
    labelled(over, "OVERLAY  (stitch / bmj dark)").save(
        os.path.join(OUT, f"{name}_overlay.png")
    )

    print(f"{name}: stitch {stitch.width}x{stitch.height} dark {dark.height} light {light.height}")

print("written to", OUT)
