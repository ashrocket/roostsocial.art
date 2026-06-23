#!/usr/bin/env python3
"""Couple on a bicycle — black papercut silhouette for the Roost scratchpad.

A romantic papercut: two figures leaning into a kiss atop a side-view
bicycle. Pure black ink. Wheels are thin rings with spokes; the frame is
thick tubes; the two riders are solid black masses.

Reference: the hand-held black paper-cut the user shared (couple kissing
on a bike). This is an iconic interpretation, not a pixel trace.
"""
import os
import math
from sim import save, save_rpaint, save_execution_manual, THICK_FRAC

BASE = os.path.dirname(os.path.abspath(__file__))
BLACK = "black"


# ----------------------------------------------------------------------
# primitives
# ----------------------------------------------------------------------
def line(mode, *pts, color=BLACK):
    return (color, mode, [(float(u), float(v)) for u, v in pts])


def ring(cu, cv, r, n=72, mode="thin", color=BLACK):
    pts = [(cu + r * math.cos(2 * math.pi * i / n),
            cv + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    return (color, mode, pts)


def spokes(cu, cv, r, count=12, mode="thin", color=BLACK, hub=0.10):
    out = []
    for i in range(count):
        a = 2 * math.pi * i / count
        out.append((color, mode, [(cu + hub * r * math.cos(a), cv + hub * r * math.sin(a)),
                                  (cu + r * math.cos(a), cv + r * math.sin(a))]))
    return out


def ell_fill(cu, cv, rx, ry, mode="thick", color=BLACK, overlap=0.55):
    """Solid filled ellipse as overlapping horizontal strokes."""
    out = []
    spacing = THICK_FRAC * overlap
    v = cv - ry
    while v <= cv + ry + 1e-9:
        t = max(-1.0, min(1.0, (v - cv) / ry))
        dh = rx * math.sqrt(max(0.0, 1 - t * t))
        if dh > 1e-4:
            out.append((color, mode, [(cu - dh, v), (cu, v), (cu + dh, v)]))
        v += spacing
    return out


def disk(cu, cv, r, **kw):
    return ell_fill(cu, cv, r, r, **kw)


def capsule(p, q, half, mode="thick", color=BLACK, overlap=0.55):
    """Filled thick limb/tube between p and q via parallel offset strokes."""
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1e-9
    nx, ny = -dy / L, dx / L
    out = []
    spacing = THICK_FRAC * overlap
    o = -half
    while o <= half + 1e-9:
        out.append((color, mode, [(x0 + nx * o, y0 + ny * o),
                                  (x1 + nx * o, y1 + ny * o)]))
        o += spacing
    return out


# ----------------------------------------------------------------------
# composition
# ----------------------------------------------------------------------
def strokes():
    S = []
    R = 0.125
    C1 = (0.285, 0.680)   # rear hub
    C2 = (0.715, 0.680)   # front hub
    BB = (0.500, 0.725)   # bottom bracket (cranks)
    ST = (0.452, 0.520)   # seat cluster (top of seat tube)
    HT = (0.602, 0.520)   # head tube top

    # --- wheels ---
    for C in (C1, C2):
        S += spokes(C[0], C[1], R, count=12)
        S.append(ring(C[0], C[1], R, mode="thin"))          # tire
        S.append(ring(C[0], C[1], R - 0.018, mode="thin"))  # rim
        S += disk(C[0], C[1], 0.012)                         # hub
    S.append(line("thin", (0.16, 0.812), (0.84, 0.812)))    # ground

    # --- frame (thick tubes) ---
    S += capsule(ST, HT, 0.006)   # top tube
    S += capsule(BB, ST, 0.006)   # seat tube
    S += capsule(BB, HT, 0.006)   # down tube
    S += capsule(BB, C1, 0.005)   # chain stay
    S += capsule(ST, C1, 0.005)   # seat stay
    S += capsule(HT, C2, 0.005)   # fork
    S += capsule(HT, (0.655, 0.495), 0.005)        # stem
    S.append(line("thick", (0.655, 0.468), (0.655, 0.522)))  # handlebar
    S.append(line("thick", BB, (0.523, 0.762)))    # crank
    S.append(line("thick", (0.523, 0.762), (0.547, 0.760)))  # pedal
    S.append(line("thick", (0.428, 0.514), (0.476, 0.514)))  # saddle

    # --- left rider: pedaling, faces right ---
    hipL = (0.452, 0.508)
    shoL = (0.508, 0.362)
    S += capsule(hipL, shoL, 0.028)                  # torso
    S += capsule((0.503, 0.348), shoL, 0.012)        # neck
    S += ell_fill(0.500, 0.298, 0.040, 0.050)        # head (oval)
    S += capsule(hipL, (0.500, 0.628), 0.015)        # thigh
    S += capsule((0.500, 0.628), BB, 0.012)          # shin -> pedal

    # --- right rider: perched on front, faces left ---
    hipR = (0.612, 0.498)
    shoR = (0.563, 0.362)
    S += capsule(hipR, shoR, 0.028)                  # torso
    S += capsule((0.583, 0.348), shoR, 0.012)        # neck
    S += ell_fill(0.586, 0.298, 0.040, 0.050)        # head (kiss gap ~0.006)
    S += capsule(hipR, (0.690, 0.560), 0.015)        # leg over front wheel

    # --- embrace (arms around each other) ---
    S += capsule(shoL, shoR, 0.012)                  # arms across shoulders
    S += capsule((0.527, 0.404), (0.547, 0.404), 0.010)  # lower clasp

    return S


if __name__ == "__main__":
    art = strokes()
    print(f"{len(art)} strokes")
    save(art, 100, f"{BASE}/bicycle_couple_100.png")
    save(art, 265, f"{BASE}/bicycle_couple_265.png", scale_to=530)
    save_rpaint(art, f"{BASE}/bicycle_couple.rpaint.json",
                title="Couple on a bicycle")
    save_execution_manual(art, f"{BASE}/bicycle_couple.scratchpad-manual.json",
                          title="Couple on a bicycle")
