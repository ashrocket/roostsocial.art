The gallery header and one row of art tiles from the roostsocial.art home page, the first screen a visitor sees.

Use this as the landing pattern for the site root (`/`). It shows the header (name, nav, and a log-in button), the real `recent` heading (site/src/index.js:389, 394) and the grid of tiles (site/src/index.js:38).

The emoji dove mark from the real header is left out of this preview, because previews carry no emoji. In the real header (site/src/index.js:56) `log in` is a plain link, gold only by the global `a` rule (site/src/index.js:32). The gold button is a v2 change (README.md Status item 5), so it is not in the real header yet. In this preview the log-in control is the primary action: gold fill, button-label text, radius-control, weight 600.

The consumer supplies: the tile art (`<img>` from the art store), the message text, tags, author handle, date, score and the badge for how the art was made. The footer copy and search box are not part of this pattern.

Do: keep the tile grid (`repeat(auto-fill, minmax(250px, 1fr))`) so the row wraps on a phone.

Do not: add a marketing hero, a large headline or a call to action that the real home page does not have. Do not put a real username, a real drawing or a real person's name in the preview. The preview uses `@username` and placeholder drawings.
