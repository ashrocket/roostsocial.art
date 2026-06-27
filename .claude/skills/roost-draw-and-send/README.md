# Roost: Draw and Send Art — Architecture & Field Notes

Deep reference for the `roost-draw-and-send` skill. `SKILL.md` is the quick
operational guide; this file is the *why* — the app's architecture, the
coordinate math, the drawing format, and the full chronology of what failed and
how each was fixed. Read this when something doesn't behave or you need to
extend the workflow.

---

## 1. What Roost is, and why it's awkward to automate

Roost is an **iOS app wrapped to run on macOS** (Mac Catalyst / "Designed for
iPad" style wrapper). That single fact drives almost every gotcha.

- `/Applications/Roost.app` is a **wrapper** with no top-level `Info.plist`. The
  real bundle is `/Applications/Roost.app/Wrapper/Rookery.app`.
- Bundle id: **`com.rookery.courier`**. `CFBundleName` = **Rookery**,
  `CFBundleDisplayName` = **Roost**. The running **process is `Rookery`**.
- At runtime it executes from a **private container**, e.g.
  `/private/var/folders/.../Wrapper/Rookery.app` — not from `/Applications`.

**Consequence — the computer-use MCP cannot drive it.** `request_access` only
scans normal `/Applications` bundles, so both `request_access("Roost")` and
`request_access("com.rookery.courier")` return **`not_installed`**. There is no
way to allowlist it for the computer-use tools.

**The workaround that does work:** ignore the computer-use MCP entirely and use
the system `python3` (which has **PIL**, **pyautogui**, and **Quartz** via
pyobjc) through the **Bash** tool:

- Mouse + keyboard → `pyautogui` and, for drawing, **Quartz CGEvent**.
- Activation → `osascript -e 'tell application id "com.rookery.courier" to activate'`.
- Screenshots → `screencapture -C -x out.png` (the `-C` shows the cursor; `-x`
  silences the shutter sound).

---

## 2. The cmux / terminal raise problem

This Claude Code session runs inside a **cmux terminal window**. While the
session is active that window **raises itself over Roost**, so a mouse click
meant for the canvas can land on the terminal instead. (Observed concretely: a
"send" click once hit the terminal showing this very transcript.)

**Fix:** activate Roost immediately before every batch of mouse actions:

```sh
osascript -e 'tell application id "com.rookery.courier" to activate'
sleep 0.7
```

`scripts/front.sh` is exactly this, and `replay_cg.py` calls it internally via
`activate()`. The 0.7 s settle matters — activation isn't instant.

---

## 3. Coordinate spaces (the source of most missed clicks)

Three spaces are in play on a 2× Retina display. Keep them straight:

| Space | Size (this setup) | Used by |
|-------|-------------------|---------|
| **Logical points** | 1440 × 900 | pyautogui, Quartz CGEvent — **the space you click in** |
| **Physical pixels** | 2880 × 1800 | `screencapture` PNG output |
| **Displayed pixels** | 2000 × 1250 | how the Read tool shows a screenshot to the agent |

Conversions:

```
logical  = physical / 2          (= physical / SCALE, SCALE ≈ 2.0)
logical  = displayed × 0.72      (1440 / 2000 = 0.72)
physical = logical × 2
```

- `measure.py` reads a **physical** PNG and prints **logical** coordinates
  (it computes `SCALE = width / 1440`, so it's robust to other resolutions).
- `act.py` lets you click off a number you read on a **displayed** screenshot;
  it multiplies by `F = 0.72`. If the Read tool ever shows screenshots at a
  different width, recompute `F = 1440 / displayed_width`.

**These coordinates are not portable between sessions.** The Roost window can be
in a different place, so the canvas box and swatch row move. **Re-run
`measure.py` every session** and paste fresh values into `replay_cg.py`. The
values currently committed there are from one specific run and are only a
starting point / example.

### Calibrating with measure.py

```sh
# Scratchpad open and fully visible:
screencapture -C -x cal.png
python3 scripts/measure.py cal.png
```

It prints the white-canvas bounding box (top-left → bottom-right) and the
centers of the six palette swatches as logical points. Paste into the
`X0,Y0,X1,Y1` line and the `SW` dict of `replay_cg.py`. Note: the detector keys
off saturation, so the **black** swatch is often missed — it's the leftmost
swatch; infer it about one swatch-spacing left of white (that's where the
committed `1142.5` came from, with white at `1186.5`).

---

## 4. Drawing: real drag events, not MouseMoved

The headline lesson. The Roost canvas builds a stroke from
`kCGEventLeftMouseDragged` events. `pyautogui.moveTo` — even between
`mouseDown()` and `mouseUp()` — emits `kCGEventMouseMoved`, which the canvas
**does not** treat as drawing. The visible result is a **dot at each polyline
vertex** and nothing in between.

`replay_cg.py` fixes this by posting real drag events and **interpolating** dense
points between each pair of vertices so the line is continuous:

```python
def post(etype, x, y):
    e = Quartz.CGEventCreateMouseEvent(None, etype, (x, y), Quartz.kCGMouseButtonLeft)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)

def stroke(P, mode):
    step  = 5.0  if mode == "thick" else 2.5     # px between interpolated points
    dwell = 0.001 if mode == "thick" else 0.012  # slower == thinner (speed-sensitive pen)
    post(Quartz.kCGEventLeftMouseDown, *P[0]); time.sleep(0.03)
    for (xa, ya), (xb, yb) in zip(P, P[1:]):
        n = max(1, int(math.hypot(xb-xa, yb-ya) / step))
        for i in range(1, n + 1):
            t = i / n
            post(Quartz.kCGEventLeftMouseDragged, xa+(xb-xa)*t, ya+(yb-ya)*t)
            time.sleep(dwell)
    post(Quartz.kCGEventLeftMouseUp, *P[-1]); time.sleep(0.09)
```

**The pen is speed-sensitive.** Drawing fast yields a thick line; drawing slowly
yields a thin one. So `mode` controls `dwell`, not a brush setting: `thin`
strokes use a longer per-point sleep (~0.012 s) and a finer interpolation step;
`thick` strokes blast through quickly. Color is chosen by **clicking the swatch**
before the stroke, and the replayer only re-clicks when the color changes.

**Always smoke-test first:** `python3 scripts/replay_cg.py --test` draws a black
diagonal, a thin baseline, and a red arc. Screenshot and confirm lines. If you
see dots, you are not running `replay_cg.py` (or Roost isn't frontmost).

`scripts/replay_roost.py` is the original pyautogui version, kept **only** as a
labeled cautionary example — the diff against `replay_cg.py` is the whole lesson.

---

## 5. The `.rpaint.json` drawing format

Art is authored in `roost_sim/` and serialized to `.rpaint.json` by
`sim.save_rpaint`. The format is intentionally tiny and resolution-independent:

```json
{
  "version": 1,
  "format": "roost-rpaint",
  "title": "Pigeon self-portrait",
  "palette": ["black", "white", "red", "blue", "green", "yellow"],
  "canvas": { "normalized": true, "background": "white" },
  "strokes": [
    ["green", "thick", [[0.2, 0.84], [0.5, 0.835], [0.8, 0.84]]],
    ["black", "thin",  [[0.345, 0.33], [0.375, 0.295], ...]]
  ]
}
```

- A stroke is `[color, mode, points]`. `color` ∈ the palette; `mode` ∈
  `{"thick","thin"}`; `points` are **normalized `[u, v]` in `[0..1]`**.
- The replayer maps each point to the live canvas:
  `x = X0 + u*(X1-X0)`, `y = Y0 + v*(Y1-Y0)`.
- Palette order is fixed: **black, white, red, blue, green, yellow**.
- Brush fractions (from `sim.py`): `THICK_FRAC = 7/265`, `THIN_FRAC = 3/265`
  (relative to a 265-px reference canvas — that's the preview render size).

### Authoring helpers in `roost_sim/sim.py`

| Function | Does |
|----------|------|
| `save_rpaint(strokes, path, title=)` | Write a `.rpaint.json` (this is what the replayer draws) |
| `save_execution_manual(strokes, path, title=)` | Write a verbose step-by-step JSON manual (calibration + per-stroke actions) |
| `save(strokes, size, path, scale_to=)` | Render a true-size PNG **and** a `_big.png` nearest-neighbour upscale |
| `render(strokes, size)` | Return a PIL image |
| `normalize_strokes(strokes)` | Clamp/clean points (`OVERDRAW_TOLERANCE = 0.05`) |
| `load_rpaint(path)` | Read strokes back from an rpaint or manual JSON |

Birds live in `roost_sim/art_portraits2.py`, registered in `PORTRAITS`:
`mockingbird, crane, owl, guillemot, pigeon_bear, pigeon_toby` (`pigeon_toby` is
a mirror of `pigeon_bear`). Add a function and a `PORTRAITS` entry to make a new
one available to `gen_art.py`.

---

## 6. The Roost UI send flow

Map of the path from a conversation to a dispatched pigeon:

1. Open a conversation in the rookery.
2. **+** (compose attachments) → **Scratchpad** → blank canvas + the 6-swatch
   palette below it.
3. Draw (calibrate → `--test` → replay the rpaint).
4. **Done** → drawing attaches to the message ("Drawing attached" + thumbnail).
5. Yellow **↑** (Send) → **Select A Bird** screen.
6. Tap a **courier pigeon** card (couriers have names + an ETA, e.g. "55h 30m").
7. **Send →** → feather dispatch animation; the conversation shows an
   **"In Flight"** badge and, later, an "Arrived" timestamp with a
   from→to route and transit time.

Each `→` step is a single click; locate the control on a fresh screenshot and
convert with `act.py` (×0.72) or click logical coordinates directly.

---

## 7. Sending is a real, outward-facing action

A dispatched pigeon is a genuine message delivered to a contact. Treat the
**send** steps (5–7 above) as requiring the user's go-ahead:

- **Drawing** on the Scratchpad is harmless — do it freely while iterating.
- **Sending** should only happen when the user asked to send and a recipient is
  chosen/authorized. The recipients here are low-stakes in-app personas (e.g.
  `@bookishmatt` presents as "Marceline from Adventure Time"), but the principle
  stands: don't dispatch on your own initiative.

---

## 8. Quick environment cheat-sheet

```sh
# bring Roost forward (run before every mouse batch)
.claude/skills/roost-draw-and-send/scripts/front.sh

# generate art  ->  /tmp/out/pigeon_bear.rpaint.json (+ manual + previews)
python3 .claude/skills/roost-draw-and-send/scripts/gen_art.py pigeon_bear /tmp/out

# calibrate from a screenshot of the open Scratchpad
screencapture -C -x cal.png
python3 .claude/skills/roost-draw-and-send/scripts/measure.py cal.png
#   -> paste CANVAS (logical) + swatches into replay_cg.py's X0,Y0,X1,Y1 / SW

# smoke-test the pen (expect lines, not dots), then draw
python3 .claude/skills/roost-draw-and-send/scripts/replay_cg.py --test
python3 .claude/skills/roost-draw-and-send/scripts/replay_cg.py /tmp/out/pigeon_bear.rpaint.json

# click off a screenshot number (displayed px -> logical)
python3 .claude/skills/roost-draw-and-send/scripts/act.py click 1737 535
```

System `python3` already has PIL + pyautogui + Quartz. No virtualenv needed
(`controller/.venv` does **not** exist — don't reach for it).
```
