#!/usr/bin/env python3
"""Generate a Roost scratchpad drawing from the repo's art functions.

Writes four files per portrait, named <portrait>.*:
  .rpaint.json   normalized [0..1] strokes  <- this is what replay_cg.py draws
  .manual.json   step-by-step execution manual (reference / computer-use replay)
  .png           true-size render (265px) for inspection
  _big.png       nearest-neighbour upscale so a tiny canvas is legible

Usage:
    python3 gen_art.py [portrait] [out_dir]

    portrait  key in art_portraits2.PORTRAITS (default: pigeon_bear)
              -> mockingbird crane owl guillemot pigeon_bear pigeon_toby
    out_dir   directory for the output files (default: this scripts/ dir)

Add new birds by editing roost_sim/art_portraits2.py (PORTRAITS dict)."""
import sys, os
from collections import Counter

REPO = "/Users/ashrocket/ashcode/roostsocial.art"
sys.path.insert(0, f"{REPO}/roost_sim")

from sim import save, save_rpaint, save_execution_manual  # noqa: E402
import art_portraits2 as ap                                # noqa: E402

portrait = sys.argv[1] if len(sys.argv) > 1 else "pigeon_bear"
out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))

if portrait not in ap.PORTRAITS:
    sys.exit(f"unknown portrait '{portrait}'. choices: {', '.join(ap.PORTRAITS)}")

art = ap.PORTRAITS[portrait]()
base = os.path.join(out_dir, portrait)
title = portrait.replace("_", " ").title() + " self-portrait"

save_rpaint(art, f"{base}.rpaint.json", title=title)
save_execution_manual(art, f"{base}.manual.json", title=title)
save(art, 265, f"{base}.png", scale_to=600)

colors = Counter(s[0] for s in art)
print(f"{portrait}: {len(art)} strokes; colors: {dict(colors)}")
print(f"wrote {base}.{{rpaint.json,manual.json,png,_big.png}}")
