#!/usr/bin/env python3
"""Self-portrait sketches for each sendable bird, ink-on-white-paper style.

Birds: Black-crowned Night Heron, Mute Swan, Golden-cheeked Warbler.
Each is a stroke list (color, thick|thin, [(u,v)...]) for the Roost pen.
"""
import os
import sys
from sim import save

BASE = os.path.dirname(os.path.abspath(__file__))


def heron():
    S = []
    # ground: green strip
    S.append(("green", "thick", [(0.15, 0.88), (0.5, 0.875), (0.85, 0.88)]))
    S.append(("green", "thin", [(0.20, 0.905), (0.5, 0.90), (0.80, 0.905)]))
    # long pointed bill (two converging thin lines)
    S.append(("black", "thin", [(0.18, 0.30), (0.27, 0.285), (0.36, 0.27)]))
    S.append(("black", "thin", [(0.18, 0.30), (0.27, 0.305), (0.36, 0.31)]))
    # black cap (thick mass on top of head) + occipital plume
    S.append(("black", "thick", [(0.37, 0.245), (0.45, 0.225), (0.52, 0.235)]))
    S.append(("black", "thick", [(0.38, 0.27), (0.46, 0.255), (0.52, 0.262)]))
    S.append(("black", "thin", [(0.52, 0.24), (0.58, 0.215), (0.64, 0.20)]))
    # head/neck/breast outline down the front
    S.append(("black", "thin", [(0.37, 0.30), (0.385, 0.36), (0.40, 0.44), (0.42, 0.54), (0.45, 0.64), (0.49, 0.715)]))
    # back of head into back
    S.append(("black", "thin", [(0.52, 0.275), (0.53, 0.33), (0.545, 0.38)]))
    # red eye
    S.append(("red", "thin", [(0.41, 0.275), (0.418, 0.272)]))
    # black back / folded wing (thick mass)
    S.append(("black", "thick", [(0.545, 0.385), (0.60, 0.42), (0.645, 0.47)]))
    S.append(("black", "thick", [(0.535, 0.42), (0.59, 0.46), (0.635, 0.515)]))
    S.append(("black", "thick", [(0.525, 0.46), (0.575, 0.50), (0.62, 0.555)]))
    # wing/tail rear outline + plume droop
    S.append(("black", "thin", [(0.645, 0.47), (0.66, 0.545), (0.655, 0.62), (0.63, 0.68)]))
    S.append(("black", "thin", [(0.60, 0.56), (0.615, 0.625), (0.60, 0.685)]))
    # belly outline to tail
    S.append(("black", "thin", [(0.49, 0.715), (0.55, 0.725), (0.61, 0.71), (0.63, 0.68)]))
    # legs (yellow) + feet
    S.append(("yellow", "thin", [(0.51, 0.725), (0.50, 0.80), (0.495, 0.875)]))
    S.append(("yellow", "thin", [(0.57, 0.72), (0.575, 0.795), (0.58, 0.875)]))
    S.append(("yellow", "thin", [(0.46, 0.88), (0.50, 0.875), (0.535, 0.88)]))
    S.append(("yellow", "thin", [(0.55, 0.88), (0.585, 0.875), (0.62, 0.88)]))
    # sky hints
    S.append(("blue", "thin", [(0.08, 0.12), (0.20, 0.115), (0.30, 0.12)]))
    S.append(("blue", "thin", [(0.70, 0.10), (0.82, 0.095), (0.92, 0.10)]))
    return S


def swan():
    S = []
    # water band
    for i, v in enumerate([0.66, 0.70, 0.74, 0.78]):
        S.append(("blue", "thick", [(0.05, v), (0.5, v - 0.005), (0.95, v)]))
    # white gap wavelets over water
    S.append(("white", "thin", [(0.15, 0.72), (0.30, 0.715), (0.45, 0.72)]))
    S.append(("white", "thin", [(0.55, 0.76), (0.70, 0.755), (0.85, 0.76)]))
    # body hull outline (floating, facing left) — white body left unpainted
    S.append(("black", "thin", [(0.30, 0.62), (0.40, 0.655), (0.55, 0.665), (0.68, 0.645), (0.74, 0.60)]))
    # raised wing puff (scalloped back)
    S.append(("black", "thin", [(0.74, 0.60), (0.72, 0.52), (0.66, 0.46), (0.58, 0.44), (0.52, 0.47), (0.50, 0.52)]))
    S.append(("black", "thin", [(0.52, 0.52), (0.56, 0.49), (0.62, 0.48)]))
    S.append(("black", "thin", [(0.55, 0.56), (0.60, 0.53), (0.66, 0.52)]))
    # chest up into S-neck (front line)
    S.append(("black", "thin", [(0.30, 0.62), (0.295, 0.55), (0.315, 0.47), (0.345, 0.41), (0.345, 0.35), (0.33, 0.30)]))
    # back of neck (parallel S)
    S.append(("black", "thin", [(0.50, 0.52), (0.43, 0.50), (0.395, 0.44), (0.39, 0.37), (0.375, 0.31), (0.355, 0.275)]))
    # head
    S.append(("black", "thin", [(0.33, 0.295), (0.335, 0.27), (0.355, 0.26), (0.375, 0.27)]))
    # orange-red bill with black knob + eye
    S.append(("red", "thin", [(0.335, 0.275), (0.305, 0.285), (0.275, 0.295)]))
    S.append(("black", "thin", [(0.336, 0.272), (0.341, 0.270)]))
    S.append(("black", "thin", [(0.352, 0.272), (0.357, 0.270)]))
    # reflection squiggle
    S.append(("blue", "thin", [(0.34, 0.70), (0.45, 0.695), (0.58, 0.70), (0.66, 0.695)]))
    return S


def warbler():
    S = []
    # branch (diagonal) + leaf dabs
    S.append(("black", "thin", [(0.16, 0.76), (0.48, 0.715), (0.82, 0.675)]))
    S.append(("green", "thick", [(0.22, 0.73), (0.275, 0.715)]))
    S.append(("green", "thick", [(0.68, 0.655), (0.735, 0.64)]))
    S.append(("green", "thick", [(0.76, 0.715), (0.81, 0.70)]))
    # connected outline: head -> chest -> belly -> tail base -> back -> head
    S.append(("black", "thin", [(0.40, 0.36), (0.41, 0.305), (0.455, 0.275), (0.505, 0.285), (0.53, 0.33)]))
    S.append(("black", "thin", [(0.40, 0.36), (0.39, 0.42), (0.40, 0.49), (0.43, 0.56), (0.47, 0.61), (0.52, 0.63), (0.57, 0.62), (0.60, 0.57)]))
    S.append(("black", "thin", [(0.53, 0.33), (0.565, 0.385), (0.59, 0.45), (0.60, 0.52), (0.60, 0.57)]))
    # tiny bill
    S.append(("black", "thin", [(0.40, 0.345), (0.352, 0.362)]))
    # yellow cheek/face
    S.append(("yellow", "thick", [(0.43, 0.345), (0.465, 0.34), (0.50, 0.345)]))
    S.append(("yellow", "thick", [(0.435, 0.375), (0.468, 0.37), (0.498, 0.375)]))
    # black cap + thin eye-line
    S.append(("black", "thick", [(0.418, 0.308), (0.46, 0.292), (0.508, 0.302)]))
    S.append(("black", "thin", [(0.42, 0.352), (0.458, 0.347), (0.492, 0.352)]))
    # black throat/bib
    S.append(("black", "thick", [(0.415, 0.40), (0.443, 0.415), (0.462, 0.432)]))
    S.append(("black", "thick", [(0.425, 0.452), (0.45, 0.468), (0.468, 0.482)]))
    # wing mass + white wingbars
    S.append(("black", "thick", [(0.52, 0.38), (0.558, 0.432), (0.588, 0.49)]))
    S.append(("black", "thick", [(0.51, 0.432), (0.548, 0.482), (0.578, 0.532)]))
    S.append(("white", "thin", [(0.528, 0.418), (0.557, 0.448), (0.58, 0.475)]))
    S.append(("white", "thin", [(0.518, 0.462), (0.545, 0.49), (0.567, 0.515)]))
    # flank streaks
    S.append(("black", "thin", [(0.455, 0.51), (0.472, 0.535)]))
    S.append(("black", "thin", [(0.468, 0.555), (0.484, 0.578)]))
    # tail
    S.append(("black", "thick", [(0.60, 0.57), (0.645, 0.62), (0.685, 0.665)]))
    S.append(("white", "thin", [(0.617, 0.605), (0.652, 0.64)]))
    # legs down to the branch
    S.append(("black", "thin", [(0.478, 0.625), (0.483, 0.668), (0.478, 0.708)]))
    S.append(("black", "thin", [(0.52, 0.63), (0.528, 0.668), (0.533, 0.702)]))
    # sky hint
    S.append(("blue", "thin", [(0.10, 0.12), (0.22, 0.115), (0.32, 0.12)]))
    return S


PORTRAITS = {"heron": heron, "swan": swan, "warbler": warbler}

if __name__ == "__main__":
    for name, fn in PORTRAITS.items():
        art = fn()
        save(art, 265, f"{BASE}/portrait_{name}.png", scale_to=400)
        print(f"{name}: {len(art)} strokes")
