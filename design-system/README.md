# Roost Social Gallery design system

roostsocial.art is a public gallery of scratchpad drawings made in the Roost carrier-pigeon messaging app. Users send art to the publish bot. Visitors browse the recent and popular art, rank chirps from 1 to 10 and add tags. The site root (`/`) is the gallery itself, not a marketing page, so its job is to show art and link to sign-up and how-to pages (site/src/index.js:4, 389-394).

## Voice

1. Say what the thing does, in one plain line. Example: "art arrives by carrier pigeon · ranks are 1–10 chirps · tags welcome" (site/src/index.js:65).
2. Use short, direct sentences. Example: "If it didn't fly here on a bird, it doesn't get published." (site/src/index.js:137).
3. Name the next step with the exact place to go. Example: "Enter it at /login — that's it, you're in" (site/src/index.js:143).
4. Use the product's own words: Roost, chirp, scratchpad, bird. Example: "rank any chirp 1–10 and add tags." (site/src/index.js:144).
5. Put no marketing words in product copy. The sign-up line states the facts: "Roost is a carrier-pigeon messaging app" (site/src/index.js:159).

## Colour

Canonical surface: the public gallery site. Values are the code values; contrast is WCAG ratio on the stated ground.

| Token | Value | Role | Contrast |
|---|---|---|---|
| `bg` | #0e1116 | Page background | ground |
| `card` | #1a212b | Tile surface | ground |
| `image-base` | #ffffff | Image ground behind art (v2 name, value unchanged) | not text |
| `ink` | #e8edf4 | Primary text | 16.08:1 on `bg`, 13.77:1 on `card` |
| `muted` | #93a1b3 | Meta line, user name, footer | 7.19:1 on `bg`, 6.16:1 on `card` |
| `gold` | #e7b63c | Links, score, primary button | 10.04:1 on `bg`, 8.6:1 on `card`, 7.06:1 on `tag` |
| `blue` | #4583d6 | Secondary accent, defined but not used on the canonical surface | 4.93:1 on `bg`, 4.22:1 on `card` (fails 4.5:1 on `card`; not used for text) |
| `button-label` | #1a1409 | Button label | 9.72:1 on `gold` |
| `tag` | #243043 | Tag pill, badge, input, notice | ink on `tag` 11.31:1 |
| `line` | #2a3340 | Hairline borders | decorative |
| `line-input` | #34425a | Input border | decorative |

## Type

Family: system stack, no web font. `-apple-system, system-ui, sans-serif` (site/src/index.js:31). Nothing is loaded from the network.

| Style | Size | Weight | Used for |
|---|---|---|---|
| body | 16px, line 1.5 | 400 | Page text (site/src/index.js:31) |
| site-title | 1.25rem | 400 | Header name (site/src/index.js:34) |
| message | 0.95rem | 400 | Art message (site/src/index.js:42) |
| meta | 0.85rem | 400 | Byline and date (site/src/index.js:41) |
| score | 0.85rem | 600 | Rank, gold (site/src/index.js:45) |
| tag | 0.8rem | 400 | Tag pills (site/src/index.js:43) |
| button | 16px | 600 | Gold buttons (site/src/index.js:48) |

## Layout and spacing

- Tile grid: `repeat(auto-fill, minmax(250px, 1fr))` with a 1rem gap (site/src/index.js:38). The row wraps on a phone.
- Page gutter: 1.2rem around the main column; main column max width 880px (site/src/index.js:37).
- Spacing steps: 0.4rem, 0.8rem, 1rem, 1.2rem (`space-sm`, `space-md`, `space-lg`, `space-xl`).
- Radius: tile 14px, image 10px, control 8px, badge 6px, pill 999px.
- No shadow on the canonical surface.

## Logo and wordmark

- The site has no logo file. Its mark is the dove emoji 🕊️ followed by the name in plain type (site/src/index.js:54).
- Wordmark: "roostsocial.art", system stack, weight 400, 1.25rem, colour `ink`, lowercase, no tracking.
- The cover (components/Cover/preview.html) sets the same wordmark at 72px, the display size that SPEC requires for covers. Its size and line length differ from the header; the words, face, weight, case and tracking do not.
- The real file in `assets/Logos/RoostDraw.icns` is the RoostDraw Mac app icon, copied with `cp` from controller/RoostDraw/Resources/RoostDraw.icns. It is not the gallery logo. Use it only for the Mac app.
- Clear space and minimum size: not defined in the source.
- Do not redraw the mark or add a new one.

## Landing page anatomy

The site root, in order (site/src/index.js:53-66, 389-394):

1. Header: emoji mark and name, nav (recent, popular, search, how-to), log-in link on the right.
2. Section heading: `recent` (h2).
3. Tile grid: one row of art tiles on desktop. Each tile: art, message, tags, byline, date, score, badge.
4. Footer: sign-up link, how-to links, Roost Paint link, one copy line.

## Status

v2. Canonical surface: the public gallery site. The brief added one decision, so the values come from code with these changes:

1. Scope: the light grey palette of the Mac viewer and drawing app is a tool surface, not part of this system. Replaces: nothing; no value changed. The values stay at roost_sim/viewer.html:10-19 and controller/RoostDraw/Sources/RoostDraw/Theme.swift:6-13. Why: the owner decided the canonical surface is the public gallery, and the tool apps are listed in Drift.
2. Token added: `image-base` = #ffffff. Replaces: the literal #fff at site/src/index.js:40. Value unchanged. Why: a named ground for art images, so previews do not hard-code a colour.
3. Hero preview: the dove emoji is left out of the header, and the badges read `iOS`, `macOS` and `Roost Paint` without their emoji. Replaces: site/src/index.js:20-22 and 54. Why: previews carry no emoji.
4. Hero preview: each meta field is its own item with a gap between items. Dot separators are not used. Replaces: the middle-dot separators of the site meta line. Why: no `A · B · C` strings in previews.
5. Hero preview: `log in` is a gold button, the one primary action. Replaces: the plain gold text link at site/src/index.js:33-36. Why: the header had no visible primary control.
6. Logo: the RoostDraw app icon is kept as the .icns, copied with `cp`. Replaces: nothing; no PNG or SVG of the icon exists in the project. Why: an extracted PNG is not byte-identical to any project file, and the brief allows the .icns when no PNG exists.

## Drift

Values on other surfaces that differ from this system. A fact, not a plan.

| Surface | Path:line | Value | This system | Difference |
|---|---|---|---|---|
| Viewer page bg | roost_sim/viewer.html:10 | #f4f5f7 | `bg` #0e1116 | light, not dark |
| Viewer panel | roost_sim/viewer.html:11 | #ffffff | `card` #1a212b | light, not dark |
| Viewer ink | roost_sim/viewer.html:13 | #15181d | `ink` #e8edf4 | dark text on light |
| Viewer muted | roost_sim/viewer.html:14 | #5b6472 | `muted` #93a1b3 | different value |
| Viewer line | roost_sim/viewer.html:15 | #c8ced8 | `line` #2a3340 | different value |
| Viewer record red | roost_sim/viewer.html:16 | #d2413c | none | no token |
| Viewer shadow | roost_sim/viewer.html:20 | 0 12px 32px rgba(21,24,29,0.12) | none | no shadow token |
| Viewer font | roost_sim/viewer.html:30 | 14px, stack with BlinkMacSystemFont and "Segoe UI" | 16px `font-sans` | size and stack differ |
| Mac app bg | controller/RoostDraw/Sources/RoostDraw/Theme.swift:6 | #f4f5f7 | `bg` #0e1116 | light, not dark |
| Mac app panel | controller/RoostDraw/Sources/RoostDraw/Theme.swift:7 | #ffffff | `card` #1a212b | light, not dark |
| Mac app ink | controller/RoostDraw/Sources/RoostDraw/Theme.swift:9 | #15181d | `ink` #e8edf4 | dark text on light |
| Mac app muted | controller/RoostDraw/Sources/RoostDraw/Theme.swift:10 | #5b6472 | `muted` #93a1b3 | different value |
| Mac app line | controller/RoostDraw/Sources/RoostDraw/Theme.swift:11 | #c8ced8 | `line` #2a3340 | different value |
| Mac app red | controller/RoostDraw/Sources/RoostDraw/Theme.swift:12 | #d2413c | none | no token |
| Mac app backdrop | controller/RoostDraw/Sources/RoostDraw/Theme.swift:13 | #dfe3e9 | none | no token |
| Project review page bg | PROJECT.html:10 | #f7f3ea | `bg` #0e1116 | warm cream |
| Project review page ink | PROJECT.html:12 | #1c222b | `ink` #e8edf4 | dark text on light |
| Project review page accent | PROJECT.html:15 | #8f3d2f | `gold` #e7b63c | different accent |
