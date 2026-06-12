# roostsocial.art

Public gallery for scratch-pad art from [Roost](https://roostsocial.app) — the
carrier-pigeon messaging app. Send your drawing by bird to **@ashrocket** and the
publish bot posts it here, tags it from your #hashtags, and flies a bird back
carrying your magic login link. Human art only.

- `site/` — Cloudflare Worker + D1 (gallery, claims, sessions, bot ingest)
- `publish.py` — the publish bot (key lives outside the repo)
- `roost_sim/` — scratch-pad paint simulator
- `tutorials/` — help page + 6 tutorial videos (3 flows × hand/tool), see `tutorials/PLAN.md`
- `controller` → [ashrocket/roostpaint](https://github.com/ashrocket/roostpaint): programmatic scratch-pad painter ("the new tool")
- `PROJECT.html` — full project summary

No invites / login birds fly until the site is live at roostsocial.art.
