# Roost Companion — help site + tutorial videos

Unofficial help site for Roost Social (roostsocial.app, "Old school messages, by pigeon").

## Content
- **How to access Drafts** — where unsent compositions live and how to resume them
- **How to draw on the scratch pad** — tools, palette, eraser, attaching to a message
- Three tutorials, each in two versions (6 videos total):
  1. Accessing Drafts            — `videos/01-drafts-hand.mp4` / `01-drafts-tool.mp4`
  2. Drawing on the scratch pad  — `videos/02-scratchpad-hand.mp4` / `02-scratchpad-tool.mp4`
  3. Attach a drawing and send   — `videos/03-send-drawing-hand.mp4` / `03-send-drawing-tool.mp4`
- "hand" = real-time mouse-driven screen recording, unedited
- "tool" = same flow, idle-scrubbed (mpdecimate 8fps) + caption overlays
  (brew ffmpeg has no drawtext — captions are PNG title cards rendered via
  headless Chrome and composited with the overlay filter)

## Hosting
Cloudflare (account 37c142de8a1651e97f99753ab0addfe6) AFTER the domain is
registered by Ashley — static site (Workers Assets or Pages) with videos as
assets. Until then: local build only, nothing deployed.

## Workflow
1. `scripts/record.sh <name> <seconds>` — capture screen while driving Roost
2. `scripts/produce.mjs <name>` — scrub + caption → the "tool" version
3. `site/` — static page linking the six videos + written how-tos

## Field notes from driving the real app (Jun 12, macOS)

### Drafts (observed behavior — verify before filming)
- Roost auto-saves an in-progress composition. Closing the bird-picker with
  Cancel returns to the compose sheet with recipient, attachment, and text intact.
- A draft survives navigating the compose flow (observed with a drawing
  attached + recipient set). To resume: reopen New Message — the draft is
  restored in place. No dedicated "Drafts" list found in the UI so far; the
  draft lives in the compose sheet itself. (Confirm whether multiple parallel
  drafts are kept — we observed two different recipients holding state.)

### Scratch pad
- Reach it from any message: + → Scratchpad. Six-color palette, speed-sensitive
  pen: fast strokes thick, slow strokes thin. macOS app is far easier to draw
  in than iOS (bigger canvas, mouse precision) — say so in the tutorial.
- Pigeon Paint (controller/) replays precise synthetic strokes for the
  tool-version videos.

### Care minigames (Rookery → bird → Care, 1 energy/session, +3 bond, 3 rounds)
Useful for a possible 4th tutorial; mechanics observed:
- Preening: stroke along the glowing circles (drag, ~arc over head + lower
  wings). Reliable 3 stars with one continuous stroke.
- Mealtime: tap repeatedly around the bird's feet to scatter seeds — 3 stars.
- Bath Time: a rain cloud follows the cursor; hold it over the bird — easy.
- Echo Song / Copycat: Simon-says note/move sequences — demo plays immediately
  at round start (recording will catch it; live agents miss it).
- Bug Chase: "lure the butterfly" — technique unsolved (cursor-follow, drag,
  and direct taps all scored 0). Watch the round demo when filming.
- Jingle: grab the bell, shake it next to the bird (fast oscillation) — partial.
