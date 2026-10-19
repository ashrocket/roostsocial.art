# Sources

Every source file read for this system, and what came from it. Paths are relative to the project root (`roostsocial.art/`). Paths outside the project start with `~/ashcode/` and are shown that way on purpose.

| File | Lines read | What came from it |
|---|---|---|
| ~/ashcode/design-systems/profiles/roostsocial.art.json | all | Surfaces, palette citations, classification (formalize_from_code) |
| ~/ashcode/design-systems/SPEC.md | all | File layout, tokens.json grammar, preview and build rules |
| ~/ashcode/design-systems/evidence/roostsocial.art.json (digest) | digest output | Cross-check of palette and font values |
| site/src/index.js | 1-200 (plus line checks by grep) | Palette (17), body and font (31), header and nav (33-36, 53-56), tile and grid (38-40), tags, badges, buttons, notice (42-51), footer copy (59-66), how-to copy (134-160), home heading (389-394) |
| controller/RoostDraw/Sources/RoostDraw/Theme.swift | 1-30 | Light Mac tool palette (6-13). Drift only. |
| roost_sim/viewer.html | 1-45 (plus grep) | Light viewer palette (10-20), body font (30). Drift only. |
| PROJECT.html | 10-20 | Warm review-page palette. Drift only. |
| controller/RoostDraw/Resources/RoostDraw.icns | binary, copied | RoostDraw Mac app icon. No PNG or SVG of it exists in the project, so the .icns was copied with `cp` to assets/Logos/RoostDraw.icns. |
| roost_sim/*.png, captures/*.png, controller/*.png | not read | Test and capture images, not used. Not copied. |
| .claude/skills/roost-draw-and-send/examples/*.png | not read | Example art, not used. Not copied. |

Logo search: `find` over the project for `*icon*`, `*logo*`, `*mark*`, `favicon*` and `apple-touch*` (excluding roost_sim, captures and node_modules) found no PNG or SVG logo or icon. The only image files are test and capture PNGs, which are not logos.

Tools run on this system: gen_tokens_css.py (writes tokens.css), validate.py, contrast.py, shot.sh (renders previews).

Not read: `.env` files, credentials, `site/wrangler.jsonc`, the D1 schema and the database file. They were not needed for these values, and no secret or personal data was copied.
