#!/usr/bin/env python3
"""Replay an .rpaint.json onto the Roost Scratchpad using REAL macOS drag
events (Quartz CGEvent kCGEventLeftMouseDragged).

WHY Quartz and not pyautogui: pyautogui.moveTo (even with the mouse button
held) emits kCGEventMouseMoved, which the Roost canvas ignores for drawing --
you get a dot at each vertex, not a line. Interpolating dense *Dragged* points
between vertices is what produces continuous strokes. This is the single most
important lesson in this skill. See replay_roost.py for the broken version.

Coordinates are LOGICAL points (the pyautogui / CGEvent coordinate space, =
physical pixels / 2 on a 2x Retina display). The X0/Y0/X1/Y1 and swatch values
below are DISPLAY- AND WINDOW-SPECIFIC. They are NOT universal -- re-derive
them with measure.py every run (the window can move between sessions):

    screencapture -C -x cal.png && python3 measure.py cal.png
    # paste the printed CANVAS (logical) + swatch logicals below

Usage:
    python3 replay_cg.py --test            # 3 calibration strokes, no art
    python3 replay_cg.py path/to.rpaint.json
"""
import json, sys, time, subprocess, math
import Quartz

# --- calibration (LOGICAL points) -- re-derive with measure.py every run ---
X0, Y0, X1, Y1 = 1073.5, 197.0, 1431.5, 555.0
SW = {
    "black":  (1142.5, 698), "white": (1186.5, 698), "red":    (1231.0, 698),
    "blue":   (1275.0, 698), "green": (1319.0, 698), "yellow": (1363.0, 698),
}


def post(etype, x, y):
    e = Quartz.CGEventCreateMouseEvent(None, etype, (x, y), Quartz.kCGMouseButtonLeft)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)


def click(x, y):
    post(Quartz.kCGEventLeftMouseDown, x, y); time.sleep(0.04)
    post(Quartz.kCGEventLeftMouseUp, x, y);   time.sleep(0.14)


def stroke(P, mode):
    step  = 5.0  if mode == "thick" else 2.5     # px between interpolated points
    dwell = 0.001 if mode == "thick" else 0.012  # slow == thin (speed-sensitive pen)
    post(Quartz.kCGEventLeftMouseDown, *P[0]); time.sleep(0.03)
    for (xa, ya), (xb, yb) in zip(P, P[1:]):
        dist = math.hypot(xb - xa, yb - ya)
        n = max(1, int(dist / step))
        for i in range(1, n + 1):
            t = i / n
            post(Quartz.kCGEventLeftMouseDragged, xa + (xb - xa) * t, ya + (yb - ya) * t)
            time.sleep(dwell)
    post(Quartz.kCGEventLeftMouseUp, *P[-1]); time.sleep(0.09)


def to_canvas(pts):
    return [(X0 + u * (X1 - X0), Y0 + v * (Y1 - Y0)) for u, v in pts]


def activate():
    # Roost must be frontmost or strokes land on the terminal/cmux window.
    subprocess.run(["osascript", "-e",
                    'tell application id "com.rookery.courier" to activate'])
    time.sleep(0.8)


if __name__ == "__main__":
    activate()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        click(*SW["black"])
        stroke(to_canvas([(0.20, 0.20), (0.80, 0.80)]), "thick")  # diagonal
        stroke(to_canvas([(0.20, 0.85), (0.80, 0.85)]), "thin")   # baseline
        click(*SW["red"])
        stroke(to_canvas([(0.25, 0.55), (0.50, 0.30), (0.75, 0.55)]), "thick")  # arc
        print("test drawn -- screenshot the canvas and confirm LINES, not dots")
    else:
        strokes = json.loads(open(sys.argv[1]).read())["strokes"]
        last = None
        for color, mode, pts in strokes:
            if color != last:
                click(*SW[color]); last = color
            stroke(to_canvas(pts), mode)
        # park the cursor off-canvas so it doesn't obscure the preview
        post(Quartz.kCGEventMouseMoved, SW["black"][0], SW["black"][1] + 40)
        print(f"drew {len(strokes)} strokes")
