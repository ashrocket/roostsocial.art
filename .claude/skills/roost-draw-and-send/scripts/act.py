#!/usr/bin/env python3
"""UI action helper for clicking through the Roost send flow.

Coordinates are given in DISPLAYED-image pixels -- the pixels you read off a
screenshot that the Read tool shows at 2000x1250 -- and converted to logical
1440x900 points via * 0.72 (F below). If your screenshot is shown at a
different displayed size, recompute F = 1440 / displayed_width.

  logical = displayed * 0.72
  physical (screencapture PNG) = logical * 2.0

Always bring Roost frontmost first (front.sh) or clicks hit the terminal.

Usage:
    ./front.sh
    python3 act.py click DX DY      # DX,DY in displayed-screenshot pixels
    python3 act.py move  DX DY
    python3 act.py type  "text"
"""
import sys, time, pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1
F = 0.72


def L(dx, dy):
    return (round(dx * F, 1), round(dy * F, 1))


cmd = sys.argv[1]
if cmd == "click":
    dx, dy = float(sys.argv[2]), float(sys.argv[3])
    pyautogui.click(*L(dx, dy))
    print("clicked disp", (dx, dy), "-> logical", L(dx, dy))
elif cmd == "move":
    dx, dy = float(sys.argv[2]), float(sys.argv[3])
    pyautogui.moveTo(*L(dx, dy))
    print("moved to logical", L(dx, dy))
elif cmd == "type":
    pyautogui.typewrite(sys.argv[2], interval=0.03)
    print("typed", sys.argv[2])
time.sleep(0.3)
