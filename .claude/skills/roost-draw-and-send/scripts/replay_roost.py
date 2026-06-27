#!/usr/bin/env python3
# ============================================================================
# DO NOT USE THIS TO DRAW. It is kept ONLY as a cautionary reference.
#
# This pyautogui version produces DOTS, not lines: pyautogui.moveTo emits
# kCGEventMouseMoved events, which the Roost canvas does not treat as drawing.
# You get one dot per polyline vertex. The fix is replay_cg.py, which posts
# real kCGEventLeftMouseDragged events with interpolated points.
#
# The only meaningful difference is the stroke loop (moveTo vs CGEvent drag) --
# everything else (calibration, swatch clicks, activate-first) is identical.
# ============================================================================
"""Replay an .rpaint.json onto the Roost Scratchpad via pyautogui. BROKEN for
drawing -- see banner above. Use scripts/replay_cg.py instead."""
import json, sys, time, subprocess
import pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

X0, Y0, X1, Y1 = 1073.5, 197.0, 1431.5, 555.0
SW = {
    "black":  (1142.5, 698), "white": (1186.5, 698), "red":    (1231.0, 698),
    "blue":   (1275.0, 698), "green": (1319.0, 698), "yellow": (1363.0, 698),
}

strokes = json.loads(open(sys.argv[1]).read())["strokes"]

subprocess.run(["osascript", "-e",
                'tell application id "com.rookery.courier" to activate'])
time.sleep(0.8)

last = None
for color, mode, pts in strokes:
    if color != last:
        pyautogui.click(*SW[color]); time.sleep(0.15); last = color
    P = [(X0 + u * (X1 - X0), Y0 + v * (Y1 - Y0)) for u, v in pts]
    pyautogui.moveTo(*P[0]); pyautogui.mouseDown(); time.sleep(0.05)
    for x, y in P[1:]:
        pyautogui.moveTo(x, y)                 # <-- emits MouseMoved => DOTS, not a line
        if mode == "thin":
            time.sleep(0.04)
    pyautogui.mouseUp(); time.sleep(0.1)

pyautogui.moveTo(SW["black"][0], SW["black"][1] + 40)
print(f"drew {len(strokes)} strokes  (as DOTS -- use replay_cg.py for real lines)")
