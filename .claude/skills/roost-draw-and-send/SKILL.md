---
name: roost-draw-and-send
description: Use when drawing, making, or sending art — a bird self-portrait, a sketch, any picture — through the Roost / Rookery carrier-pigeon messaging app on macOS, or automating its Scratchpad drawing canvas. Triggers include "send a drawing in Roost", strokes rendering as dots instead of lines, computer-use request_access returning not_installed for Roost, or mouse clicks landing on the terminal instead of the app.
---

# Roost: Draw and Send Art

## Overview

Roost (process/app name "Rookery") is a carrier-pigeon-themed messaging app. This
skill draws a picture on its **Scratchpad** canvas and sends it to a contact in
the user's **rookery**. The art is authored as normalized strokes in
`roost_sim/`, then replayed onto the live canvas with real macOS mouse events.

**The one insight that makes drawing work:** the canvas only renders **real drag
events** (Quartz `kCGEventLeftMouseDragged`). `pyautogui.moveTo` emits
`MouseMoved`, which the canvas treats as nothing — you get a dot per vertex, not
a line. Everything else here is calibration and UI navigation around that fact.

## The five things that will burn you

These were each discovered the hard way. Read them before touching the app.

| # | Gotcha | What to do instead |
|---|--------|--------------------|
| 1 | **computer-use can't allowlist Roost.** `request_access("Roost")` and `("com.rookery.courier")` both return `not_installed` — it's an iOS app wrapped for Mac, living in a private container, not a normal `/Applications` bundle. | Don't use the computer-use MCP. Drive the mouse with **`python3` + Quartz/pyautogui via Bash**, and screenshot with `screencapture`. |
| 2 | **Strokes render as dots, not lines.** `pyautogui.moveTo` (even with the button held) sends `MouseMoved`. | Use `scripts/replay_cg.py` — it posts `kCGEventLeftMouseDragged` with interpolated points. `scripts/replay_roost.py` is the broken version, kept only as a warning. |
| 3 | **Clicks land on the terminal, not Roost.** The cmux/terminal window hosting this session raises itself over Roost while the session is active. | Run `scripts/front.sh` (activates `com.rookery.courier`) at the start of **every** action batch — the replayer does this itself. |
| 4 | **Coordinates are display- and window-specific.** Hardcoded pixels from a past run will miss. Three coordinate spaces are in play: logical (CGEvent/pyautogui) = displayed-screenshot-px × 0.72 = physical-PNG-px ÷ 2. | Re-derive the canvas box + swatches with `scripts/measure.py` every run. Use `scripts/act.py` to click off a screenshot (it applies ×0.72). |
| 5 | **Sending is outward-facing.** A dispatched pigeon is a real message to a contact. | Draw freely, but only run the **send** steps when the user has asked to send / authorized a recipient. |

## Workflow

Run everything from the repo root (`/Users/ashrocket/ashcode/roostsocial.art`).
Scripts live in `.claude/skills/roost-draw-and-send/scripts/` (referred to as
`scripts/` below). Make sure Roost is open on a conversation first.

1. **Generate the art.** `python3 scripts/gen_art.py pigeon_bear /tmp/out` →
   writes `<name>.rpaint.json` (+ manual, preview PNGs). Inspect the `_big.png`.
   Birds available: `mockingbird crane owl guillemot pigeon_bear pigeon_toby`
   (edit `roost_sim/art_portraits2.py` to add more). A ready-made
   `examples/pigeon_bear.rpaint.json` is bundled if you want to skip this.
2. **Open the Scratchpad.** In the conversation: **+** → **Scratchpad**. Screenshot
   with `screencapture -C -x cal.png`.
3. **Calibrate.** `python3 scripts/measure.py cal.png` → paste the printed
   `CANVAS (logical)` corners and swatch logicals into `scripts/replay_cg.py`
   (the `X0,Y0,X1,Y1` and `SW` block). Black is the leftmost swatch; if
   `measure.py` misses it, infer it one spacing left of white.
4. **Smoke-test the pen.** `python3 scripts/replay_cg.py --test`, then
   screenshot and confirm you see continuous **lines** (a diagonal, a baseline,
   a red arc) — not dots. If dots: you're not on `replay_cg.py`, or Roost
   isn't frontmost. Clear the canvas before the real draw.
5. **Draw.** `python3 scripts/replay_cg.py /tmp/out/pigeon_bear.rpaint.json`.
   Screenshot and confirm the picture.
6. **Attach.** Tap **Done** → the drawing attaches to the message ("Drawing
   attached" + thumbnail).
7. **Send (only if authorized).** Tap the yellow **↑** Send → **Select A Bird**
   → tap a courier pigeon card → **Send →**. A feather animation + an
   "In Flight" badge on the conversation confirm dispatch.

## Scripts

| File | Purpose |
|------|---------|
| `scripts/gen_art.py` | Art function → `.rpaint.json` + execution manual + preview PNGs |
| `scripts/measure.py` | Screenshot → canvas bbox + swatch centers (logical points) |
| `scripts/replay_cg.py` | **The replayer.** Quartz drag events → real strokes. `--test` mode included |
| `scripts/act.py` | Click/move/type off a screenshot (`displayed_px × 0.72 → logical`) |
| `scripts/front.sh` | Bring Roost frontmost (run before every batch) |
| `scripts/replay_roost.py` | Broken pyautogui version — cautionary reference only |
| `examples/pigeon_bear.rpaint.json` | Ready-to-replay rock-dove self-portrait |

## More detail

- **Architecture, coordinate math, the rpaint format, and the full chronology of
  what failed and why** → `README.md` in this skill folder.
- **A copy-paste prompt to resume or repeat this from a fresh session** →
  `RESTART_PROMPT.md`.
