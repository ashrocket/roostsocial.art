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
