#!/usr/bin/env python3
"""Convert the artwork stroke list into computer_batch action JSON.

Usage: python3 emit.py X0 Y0 X1 Y1   (screen rect of the scratchpad canvas)
Writes batches/batch_NN.json, breaking only at stroke boundaries.
"""
import json
import os
import sys
import importlib

SWATCH = {  # screen coords of the color swatches — recalibrated at runtime
    # filled in by emit() from the canvas rect: swatches sit below the canvas
}

MAX_ACTIONS = 64


def emit(art, x0, y0, x1, y1, swatches):
    batches, cur = [], []
    last_color = None

    def flush():
        nonlocal cur
        if cur:
            batches.append(cur)
            cur = []

    for color, mode, pts in art:
        acts = []
        if color != last_color:
            acts.append({"action": "left_click", "coordinate": swatches[color]})
            last_color = color
        px = [[round(x0 + u * (x1 - x0)), round(y0 + v * (y1 - y0))] for u, v in pts]
        acts.append({"action": "mouse_move", "coordinate": px[0]})
        acts.append({"action": "left_mouse_down"})
        if mode == "thin":
            acts.append({"action": "wait", "duration": 0.05})
        for p in px[1:]:
            acts.append({"action": "mouse_move", "coordinate": p})
            if mode == "thin":
                acts.append({"action": "wait", "duration": 0.04})
        acts.append({"action": "left_mouse_up"})
        acts.append({"action": "wait", "duration": 0.1})
        if len(cur) + len(acts) > MAX_ACTIONS:
            flush()
            # batch boundary: re-assert color at start of next batch is not
            # needed (app keeps the selection), so just continue
        cur.extend(acts)
    flush()

    os.makedirs("batches", exist_ok=True)
    for i, b in enumerate(batches, 1):
        with open(f"batches/batch_{i:02d}.json", "w") as f:
            json.dump(b, f)
    total = sum(len(b) for b in batches)
    print(f"{len(batches)} batches, {total} actions, {len(art)} strokes")


if __name__ == "__main__":
    # usage: emit.py module.func X0 Y0 X1 Y1 [swatches-json]
    mod_name, fn_name = sys.argv[1].split(".")
    art = getattr(importlib.import_module(mod_name), fn_name)()
    if not isinstance(art, list):
        raise SystemExit("portrait fn must return stroke list")
    x0, y0, x1, y1 = map(float, sys.argv[2:6])
    # swatch row: black, white, red, blue, green, yellow (from app layout)
    sw = json.loads(sys.argv[6]) if len(sys.argv) > 6 else {
        "black": [580, 556], "white": [613, 556], "red": [646, 556],
        "blue": [679, 556], "green": [711, 556], "yellow": [744, 556],
    }
    emit(art, x0, y0, x1, y1, sw)
