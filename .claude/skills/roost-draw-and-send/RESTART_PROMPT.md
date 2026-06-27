# Restart Prompt — Draw & Send Bird Art via Roost

Paste the block below into a fresh Claude Code session in
`/Users/ashrocket/ashcode/roostsocial.art` to repeat or resume this task. It
primes the essentials and points at the skill so you don't re-learn the gotchas.

---

```
Make and send a self-portrait of a bird to someone in my rookery via the Roost app.

Load the repo-local skill `roost-draw-and-send` first (.claude/skills/roost-draw-and-send/)
— it has the full workflow, the working scripts, and the gotchas. The essentials:

- Roost is an iOS app wrapped for Mac (bundle id com.rookery.courier, process "Rookery").
  The computer-use MCP CANNOT allowlist it (request_access returns not_installed).
  Drive it with system python3 (has PIL + pyautogui + Quartz) via Bash, and
  screenshot with `screencapture -C -x`.

- Bring Roost frontmost before EVERY mouse batch (scripts/front.sh) — the terminal
  window raises over it otherwise and clicks miss.

- Draw with scripts/replay_cg.py (Quartz kCGEventLeftMouseDragged). Do NOT use
  pyautogui.moveTo to draw — it emits MouseMoved and you get dots, not lines.

- Coordinates are display-specific. Re-calibrate every run: screencapture the open
  Scratchpad, run scripts/measure.py on it, paste the canvas box + swatch logicals
  into replay_cg.py. (logical = displayed-px × 0.72 = physical-px ÷ 2.)

Steps: gen_art.py -> open Scratchpad (+ -> Scratchpad) -> measure.py calibrate ->
replay_cg.py --test (confirm LINES) -> replay_cg.py <art>.rpaint.json -> Done (attach)
-> ↑ Send -> Select A Bird -> pick a courier -> Send →. Confirm with a screenshot at
each step. Sending is a real message — only dispatch once I've okayed it.

Available birds (roost_sim/art_portraits2.py): mockingbird crane owl guillemot
pigeon_bear pigeon_toby. A ready-made examples/pigeon_bear.rpaint.json is bundled.
```

---

## Notes for whoever resumes

- **Prerequisite:** Roost must be open on a conversation. If it isn't, ask the
  user to launch it (you can't allowlist it for computer-use to launch it
  yourself; `open -b com.rookery.courier` may work from Bash).
- **First completed run:** a rock-dove (`pigeon_bear`) self-portrait was drawn on
  the Scratchpad and dispatched to `@bookishmatt`. Confirmed by the "In Flight"
  badge on the conversation.
- **If strokes look wrong:** 99% of the time it's (a) stale calibration — re-run
  `measure.py`; (b) Roost not frontmost — run `front.sh`; or (c) accidentally
  running `replay_roost.py` instead of `replay_cg.py`.
- **Full background:** `README.md` in this folder.
