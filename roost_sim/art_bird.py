#!/usr/bin/env python3
"""The artwork: swallow in flight chasing a moth (after the reference photo).

v2: broader wing blades, plumper body, prominent white throat bib,
fanned tail, better moth.
"""
import os
from sim import render, save, THICK_FRAC

BASE = os.path.dirname(os.path.abspath(__file__))


def hfill(color, mode, v0, v1, u0=0.0, u1=1.0, overlap=0.62):
    out = []
    spacing = THICK_FRAC * overlap
    v = v0
    while v <= v1 + 1e-9:
        out.append((color, mode, [(u0, v), ((u0 + u1) / 2, v), (u1, v)]))
        v += spacing
    return out


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def blade(lead, trail, n_fill):
    """Wing blade: leading edge, trailing edge, n_fill interpolated ribs."""
    S = [("black", "thick", lead), ("black", "thick", trail)]
    m = min(len(lead), len(trail))
    for i in range(1, n_fill + 1):
        t = i / (n_fill + 1)
        rib = [lerp(lead[k], trail[k], t) for k in range(m)]
        S.append(("black", "thick", rib))
    return S


def strokes():
    S = []

    # --- 1. background ---------------------------------------------------
    S += hfill("blue", "thick", 0.01, 0.99)

    # --- 2. light + ledge at the bottom ----------------------------------
    S.append(("white", "thin", [(0.0, 0.875), (0.5, 0.87), (1.0, 0.875)]))
    S += hfill("white", "thick", 0.93, 0.995)
    S.append(("blue", "thin", [(0.0, 0.96), (0.5, 0.955), (1.0, 0.96)]))

    # --- 3. bird ----------------------------------------------------------
    # left wing: broad at the shoulder, tapering to a high tip
    lead_L = [(0.385, 0.52), (0.325, 0.41), (0.27, 0.30), (0.235, 0.18), (0.215, 0.07)]
    trail_L = [(0.45, 0.56), (0.395, 0.47), (0.335, 0.36), (0.27, 0.235), (0.225, 0.09)]
    S += blade(lead_L, trail_L, 6)

    # right wing
    lead_R = [(0.445, 0.50), (0.505, 0.38), (0.55, 0.26), (0.59, 0.13), (0.615, 0.03)]
    trail_R = [(0.505, 0.545), (0.56, 0.44), (0.59, 0.325), (0.61, 0.19), (0.62, 0.05)]
    S += blade(lead_R, trail_R, 6)

    # body: plump black mass shoulders -> belly
    for i in range(8):
        u0 = 0.395 + i * 0.014
        S.append(("black", "thick", [(u0, 0.535 + i*0.002),
                                     (u0 + 0.008, 0.61),
                                     (u0 - 0.01 + (0.02 if i < 4 else 0.0), 0.68 - i*0.004),
                                     (u0 - 0.02, 0.715 - i*0.008)]))
    # head: black cap, pointing right at the moth
    S.append(("black", "thick", [(0.475, 0.545), (0.515, 0.542), (0.548, 0.553)]))
    S.append(("black", "thick", [(0.478, 0.568), (0.52, 0.566), (0.553, 0.572)]))
    S.append(("black", "thick", [(0.49, 0.588), (0.525, 0.588), (0.548, 0.588)]))
    # open beak toward the moth (two diverging spikes)
    S.append(("black", "thin", [(0.553, 0.562), (0.605, 0.538)]))
    S.append(("black", "thin", [(0.553, 0.58), (0.60, 0.612)]))

    # tail: fan of streamers sweeping down-left
    S.append(("black", "thick", [(0.395, 0.70), (0.32, 0.78), (0.24, 0.85), (0.18, 0.885)]))
    S.append(("black", "thick", [(0.405, 0.715), (0.34, 0.80), (0.275, 0.87), (0.225, 0.91)]))
    S.append(("black", "thin", [(0.415, 0.725), (0.365, 0.815), (0.32, 0.885), (0.29, 0.925)]))
    S.append(("black", "thin", [(0.425, 0.73), (0.39, 0.82), (0.36, 0.895)]))

    # --- 4. white details --------------------------------------------------
    # throat / chest bib: bright and prominent under the head
    bib_rows = [(0.607, 0.468, 0.545), (0.624, 0.462, 0.54), (0.641, 0.456, 0.53),
                (0.658, 0.45, 0.516), (0.675, 0.446, 0.50), (0.69, 0.443, 0.482),
                (0.704, 0.44, 0.464)]
    for v, ua, ub in bib_rows:
        S.append(("white", "thick", [(ua, v), ((ua+ub)/2, v - 0.004), (ub, v)]))
    # feather highlights along the wings
    S.append(("white", "thin", [(0.41, 0.535), (0.353, 0.435), (0.297, 0.325), (0.248, 0.205), (0.219, 0.078)]))
    S.append(("white", "thin", [(0.49, 0.522), (0.532, 0.41), (0.57, 0.293), (0.60, 0.16), (0.617, 0.04)]))
    S.append(("white", "thin", [(0.435, 0.55), (0.378, 0.455), (0.318, 0.345), (0.262, 0.225)]))
    # tail top-edge highlight
    S.append(("white", "thin", [(0.392, 0.69), (0.315, 0.77), (0.235, 0.84)]))

    # --- 5. moth ------------------------------------------------------------
    S.append(("white", "thick", [(0.70, 0.585), (0.675, 0.555)]))
    S.append(("white", "thick", [(0.712, 0.582), (0.712, 0.548)]))
    S.append(("white", "thick", [(0.724, 0.585), (0.748, 0.557)]))
    S.append(("white", "thick", [(0.702, 0.617), (0.678, 0.642)]))
    S.append(("white", "thick", [(0.722, 0.618), (0.745, 0.64)]))
    S.append(("black", "thin", [(0.70, 0.60), (0.726, 0.598)]))
    S.append(("white", "thin", [(0.698, 0.594), (0.682, 0.578)]))
    return S


if __name__ == "__main__":
    art = strokes()
    print(f"{len(art)} strokes")
    save(art, 100, f"{BASE}/bird_100.png")
    save(art, 265, f"{BASE}/bird_265.png", scale_to=530)
