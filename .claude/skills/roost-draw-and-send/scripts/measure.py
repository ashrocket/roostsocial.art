#!/usr/bin/env python3
"""Detect the Scratchpad white canvas bbox and the 6 color swatch centers
from a `screencapture` PNG, and print them as LOGICAL points ready to paste
into replay_cg.py.

The PNG is physical pixels (e.g. 2880x1800); the CGEvent/pyautogui coordinate
space is logical points = physical / 2 on a 2x Retina display. SCALE below
handles any ratio. Run this every session -- the window can move.

Usage:
    screencapture -C -x cal.png    # with the open Scratchpad visible
    python3 measure.py cal.png
"""
import sys
from PIL import Image

PNG = sys.argv[1]
im = Image.open(PNG).convert("RGB")
W, H = im.size
px = im.load()
SCALE = W / 1440.0  # physical / logical  (~2.0)
print(f"png size: {W}x{H}   physical/logical scale: {SCALE:.3f}")

# --- white canvas bbox: search the right-side window area ---
x_lo, x_hi = int(W * 0.74), W - 2
y_lo, y_hi = int(H * 0.18), int(H * 0.66)
minx, miny, maxx, maxy = W, H, 0, 0
step = 2
for y in range(y_lo, y_hi, step):
    for x in range(x_lo, x_hi, step):
        r, g, b = px[x, y]
        if r > 245 and g > 245 and b > 245:
            if x < minx: minx = x
            if y < miny: miny = y
            if x > maxx: maxx = x
            if y > maxy: maxy = y
print("\nCANVAS (physical px):", (minx, miny), "->", (maxx, maxy), f"  {maxx-minx}x{maxy-miny}")
print("CANVAS (logical/pyautogui):",
      (round(minx / SCALE, 1), round(miny / SCALE, 1)), "->",
      (round(maxx / SCALE, 1), round(maxy / SCALE, 1)))

# --- swatch centers: scan a horizontal band below the canvas ---
PAL = {
    "black": (17, 17, 17), "white": (255, 255, 255), "red": (210, 65, 60),
    "blue": (69, 131, 214), "green": (93, 158, 88), "yellow": (231, 182, 60),
}
band_y = int((maxy + (H - 1)) / 2)  # midway between canvas bottom and window bottom
best_y, best_score = band_y, -1
for y in range(maxy + 10, min(H - 1, maxy + int(0.18 * H)), 3):
    score = 0
    for x in range(x_lo, x_hi, 3):
        r, g, b = px[x, y]
        mx, mn = max(r, g, b), min(r, g, b)
        if mx - mn > 60: score += 1   # saturated (red/blue/green/yellow)
    if score > best_score:
        best_score, best_y = score, y
print(f"\nswatch band y (physical): {best_y}")


def col_at(x):
    rs = gs = bs = n = 0
    for dy in range(-6, 7, 2):
        r, g, b = px[x, best_y + dy]; rs += r; gs += g; bs += b; n += 1
    return (rs // n, gs // n, bs // n)


cols = []
x = x_lo
while x < x_hi:
    c = col_at(x)
    if max(c) > 60:                  # start of a swatch blob
        x0 = x
        while x < x_hi and max(col_at(x)) > 55:
            x += 1
        if x - x0 > 14:              # wide enough to be a swatch
            cx = (x0 + x) // 2
            cols.append((cx, col_at(cx)))
    x += 3

print(f"\nfound {len(cols)} swatch blobs (black may be missed -- it's the leftmost; "
      f"infer it one spacing left of white):")
for cx, c in cols:
    name = min(PAL, key=lambda k: sum((c[i] - PAL[k][i]) ** 2 for i in range(3)))
    print(f"  logical ({round(cx / SCALE, 1)}, {round(best_y / SCALE, 1)})  color~{c}  -> {name}")
