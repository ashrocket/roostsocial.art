#!/usr/bin/env python3
"""Test library for the Roost canvas simulator.

Each test is a named stroke list (normalized coords). Run at 40x40 and
100x100 to learn what survives at each resolution before attempting art.
"""
import math
import os
from sim import render, save, contact_sheet


def hfill(color, mode, v0, v1, n, u0=0.02, u1=0.98):
    """n horizontal strokes filling band v0..v1 — the basic fill primitive."""
    out = []
    for i in range(n):
        v = v0 + (v1 - v0) * i / max(1, n - 1)
        out.append((color, mode, [(u0, v), ((u0 + u1) / 2, v), (u1, v)]))
    return out


def circle(color, mode, cx, cy, r, n=16):
    pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
           for i in range(n + 1)]
    return [(color, mode, pts)]


TESTS = {}

# 1. thick horizontal lines, generous spacing — do gaps show?
TESTS["hlines_thick"] = hfill("blue", "thick", 0.1, 0.9, 6)

# 2. thin horizontal lines
TESTS["hlines_thin"] = hfill("black", "thin", 0.1, 0.9, 9)

# 3. solid fill attempt: thick lines spaced ~one stroke-width apart
TESTS["solid_fill"] = hfill("green", "thick", 0.03, 0.97, 24)

# 4. cross + diagonals — line quality off-axis
TESTS["diagonals"] = [
    ("black", "thick", [(0.1, 0.1), (0.9, 0.9)]),
    ("red", "thick", [(0.9, 0.1), (0.1, 0.9)]),
    ("blue", "thin", [(0.5, 0.05), (0.5, 0.95)]),
    ("green", "thin", [(0.05, 0.5), (0.95, 0.5)]),
]

# 5. circle outlines thick + thin
TESTS["circles"] = circle("black", "thick", 0.5, 0.5, 0.35) + \
    circle("red", "thin", 0.5, 0.5, 0.2)

# 6. palette bars
TESTS["palette"] = [
    (c, "thick", [(0.05, v), (0.95, v)])
    for c, v in zip(["black", "red", "blue", "green", "yellow"],
                    [0.15, 0.32, 0.49, 0.66, 0.83])
]

# 7. layering: blue fill, white shape on top, black outline on top of that
TESTS["layering"] = (
    hfill("blue", "thick", 0.03, 0.97, 24)
    + hfill("white", "thick", 0.40, 0.60, 5, u0=0.25, u1=0.75)
    + circle("black", "thin", 0.5, 0.5, 0.28, n=20)
)

# 8. tiny glyphs: bird "v"s — smallest readable mark
TESTS["bird_glyphs"] = [
    ("black", "thin", [(0.2, 0.3), (0.3, 0.2), (0.4, 0.3)]),
    ("black", "thick", [(0.55, 0.55), (0.68, 0.42), (0.81, 0.55)]),
]

# 9. S-curve (slow polyline smoothness)
TESTS["s_curve"] = [(
    "red", "thin",
    [(0.7, 0.15), (0.45, 0.1), (0.3, 0.25), (0.45, 0.42), (0.6, 0.55),
     (0.45, 0.75), (0.25, 0.85), (0.5, 0.92)]
)]

# 10. heart
TESTS["heart"] = [(
    "red", "thick",
    [(0.5, 0.35), (0.38, 0.2), (0.22, 0.25), (0.18, 0.42), (0.3, 0.6),
     (0.5, 0.8), (0.7, 0.6), (0.82, 0.42), (0.78, 0.25), (0.62, 0.2), (0.5, 0.35)]
)]

# 11. gradient bands — sky/water layout primitives
TESTS["bands"] = (
    hfill("blue", "thick", 0.03, 0.45, 11)
    + hfill("green", "thick", 0.48, 0.8, 8)
    + hfill("white", "thick", 0.84, 0.97, 4)
)

# 12. feather strokes — long tapering curves like a wing
TESTS["feathers"] = [
    ("black", "thick", [(0.85, 0.85), (0.6, 0.6), (0.4, 0.35), (0.3, 0.15)]),
    ("black", "thin", [(0.88, 0.78), (0.65, 0.52), (0.48, 0.3), (0.4, 0.12)]),
    ("white", "thin", [(0.8, 0.82), (0.55, 0.55), (0.36, 0.3), (0.27, 0.13)]),
]


def run(size, outdir):
    os.makedirs(outdir, exist_ok=True)
    imgs, labels = [], []
    for name, strokes in TESTS.items():
        img = save(strokes, size, f"{outdir}/{name}.png")
        imgs.append(img)
        labels.append(name)
    contact_sheet(imgs, labels, cols=4, path=f"{outdir}/_sheet.png")
    print(f"{size}x{size}: {len(TESTS)} tests -> {outdir}/_sheet.png")


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    run(40, f"{base}/tests_40")
    run(100, f"{base}/tests_100")
