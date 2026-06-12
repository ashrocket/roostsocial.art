/**
 * roostsocial.art — gallery for Roost scratchpad art ("chirps").
 *
 * Feeds: / (recent), /popular, /search?q=
 * Auth: magic claim links delivered by reply-bird inside the Roost app.
 *       Usernames are locked to Roost handles; only logged-in users can
 *       rank (1-10) or tag other people's chirps.
 * Bot:  POST /api/chirps with X-Bot-Key publishes a new chirp and returns
 *       the claim/login URL to send back to the artist.
 */

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const PALETTE = { bg: "#0e1116", card: "#1a212b", ink: "#e8edf4", dim: "#93a1b3", gold: "#e7b63c", blue: "#4583d6" };

function page(title, body, user) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · roostsocial.art</title>
<style>
  :root{color-scheme:dark}
  body{font:16px/1.5 -apple-system,system-ui,sans-serif;background:${PALETTE.bg};color:${PALETTE.ink};margin:0}
  a{color:${PALETTE.gold};text-decoration:none} a:hover{text-decoration:underline}
  header{display:flex;gap:1rem;align-items:baseline;padding:1rem 1.2rem;border-bottom:1px solid #2a3340;flex-wrap:wrap}
  header h1{font-size:1.25rem;margin:0} header h1 a{color:${PALETTE.ink}}
  nav{display:flex;gap:.9rem;flex-wrap:wrap}
  .who{margin-left:auto;color:${PALETTE.dim};font-size:.9rem}
  main{max-width:880px;margin:0 auto;padding:1.2rem}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:1rem}
  .chirp{background:${PALETTE.card};border-radius:14px;padding: .8rem;border:1px solid #2a3340}
  .chirp img{width:100%;border-radius:10px;background:#fff}
  .meta{font-size:.85rem;color:${PALETTE.dim};margin-top:.5rem}
  .msg{margin:.4rem 0;font-size:.95rem;white-space:pre-wrap}
  .tags a{display:inline-block;background:#243043;border-radius:999px;padding:.05rem .6rem;margin:.15rem .2rem 0 0;font-size:.8rem}
  .score{color:${PALETTE.gold};font-weight:600}
  form.inline{display:inline-flex;gap:.4rem;align-items:center;margin-top:.5rem;flex-wrap:wrap}
  input,select,button{font:inherit;background:#243043;color:${PALETTE.ink};border:1px solid #34425a;border-radius:8px;padding:.25rem .6rem}
  button{background:${PALETTE.gold};color:#1a1409;border:none;cursor:pointer;font-weight:600}
  footer{border-top:1px solid #2a3340;margin-top:2rem;padding:1.2rem;color:${PALETTE.dim};font-size:.85rem;text-align:center}
  .search{width:min(420px,90%)}
</style></head><body>
<header>
  <h1><a href="/">🕊️ roostsocial.art</a></h1>
  <nav><a href="/">recent</a> <a href="/popular">popular</a> <a href="/search">search</a> <a href="/how-to">how-to</a></nav>
  <span class="who">${user ? `logged in as <b>@${esc(user)}</b>` : `<a href="/how-to#login">not logged in</a>`}</span>
</header>
<main>${body}</main>
<footer>
  <p><b>Get Roost</b>: <a href="/roost-signup">sign up for the Roost app</a> ·
  <a href="/how-to#art">how to use the scratchpad art feature</a> ·
  <a href="/how-to#publish">send your art to the publish bot</a> ·
  <a href="/controller.zip">download the open-source controller</a> · <a href="https://github.com/ashrocket/roostpaint">GitHub</a> (<a href="/how-to#controller">MS&nbsp;Paint-style control of the scratchpad</a>)</p>
  <p>art arrives by carrier pigeon · ranks are 1–10 chirps · tags welcome</p>
</footer>
</body></html>`;
}

function chirpCard(c, detail = false) {
  const tags = (c.tags || "").split(",").filter(Boolean)
    .map((t) => `<a href="/search?q=%23${encodeURIComponent(t)}">#${esc(t)}</a>`).join(" ");
  const score = c.votes ? `<span class="score">${Number(c.avg).toFixed(1)}/10</span> · ${c.votes} chirp${c.votes == 1 ? "" : "s"}` : "unranked";
  return `<div class="chirp">
    ${detail ? "" : `<a href="/chirp/${c.id}">`}<img src="/img/${esc(c.image_key)}" alt="scratchpad art by @${esc(c.username)}">${detail ? "" : "</a>"}
    <div class="msg">${esc(c.message)}</div>
    <div class="tags">${tags}</div>
    <div class="meta">by <a href="/search?q=%40${encodeURIComponent(c.username)}">@${esc(c.username)}</a> · ${esc((c.created_at || "").slice(0, 16))} · ${score}</div>
  </div>`;
}

const FEED_SQL = `
  SELECT c.*, COALESCE(AVG(r.score),0) avg, COUNT(r.score) votes,
    (SELECT GROUP_CONCAT(DISTINCT tag) FROM chirp_tags t WHERE t.chirp_id=c.id) tags
  FROM chirps c LEFT JOIN ratings r ON r.chirp_id=c.id`;

async function getUser(req, env) {
  const cookie = req.headers.get("Cookie") || "";
  const m = cookie.match(/rs_session=([A-Za-z0-9-]+)/);
  if (!m) return null;
  const row = await env.DB.prepare("SELECT username FROM sessions WHERE token=?").bind(m[1]).first();
  return row ? row.username : null;
}

const HOWTO = `
<h2>How roostsocial.art works</h2>
<p id="art"><b>1. Make art in Roost.</b> In the Roost app, open any message and tap <i>+ → Scratchpad</i>.
Draw with the six-color pen, then attach it to a message. Tip: the pen is speed-sensitive — fast strokes are thick, slow strokes are thin.</p>
<p id="publish"><b>2. Send it to the publish bot.</b> Send your scratchpad drawing by bird to <b>@ashrocket</b>.
Anything you put in the message text is published with it, and any <b>#hashtags</b> become tags.
A bird will fly back to you carrying your personal login link.</p>
<p id="login"><b>3. Log in and join the flock.</b> Open the link from the return bird — it creates your account automatically.
Account names are locked to Roost usernames, so you are always @you here too. Logged-in users can rank any chirp 1–10 and add tags.</p>
<p id="controller"><b>4. Pro tools.</b> Drawing with a trackpad is hard. The open-source
<a href="https://github.com/ashrocket/roostpaint">RoostPaint controller</a> (<a href="/controller.zip">direct download</a>) gives you MS&nbsp;Paint-style tools (lines, rectangles, ellipses, undo, the exact Roost palette)
and replays your drawing onto the real scratchpad with precise synthetic strokes. Unzip, read the README, run <code>python3 roostpaint.py</code> on macOS.
The secret to drawing well on the scratchpad is using the macOS app instead of the iOS app.</p>
<p id="signup"><b>Get Roost:</b> Roost is in beta — <a href="/roost-signup">sign-up details here</a>.</p>`;

const SIGNUP = `
<h2>Get the Roost app</h2>
<p>Roost is a carrier-pigeon messaging app — your messages travel as birds, in real time, across a real map.</p>
<p>It is currently in invite-only beta. Ask <b>@ashrocket</b> for a TestFlight invite
(send a bird, or failing that, an email). When the public TestFlight link lands it will live right here.</p>
<p>Once you're in: <a href="/how-to">here's how to make and publish scratchpad art</a>.</p>`;

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const p = url.pathname;
    const user = await getUser(req, env);

    try {
      // ---------- images ----------
      if (p.startsWith("/img/")) {
        const obj = await env.ART.get(p.slice(5));
        if (!obj) return new Response("not found", { status: 404 });
        return new Response(obj.body, { headers: { "Content-Type": "image/png", "Cache-Control": "public, max-age=31536000, immutable" } });
      }

      // ---------- controller download ----------
      if (p === "/controller.zip") {
        const obj = await env.ART.get("dist/roostpaint.zip");
        if (!obj) return new Response("controller build not uploaded yet — check back soon", { status: 404 });
        return new Response(obj.body, { headers: { "Content-Type": "application/zip", "Content-Disposition": 'attachment; filename="roostpaint.zip"' } });
      }

      // ---------- static-ish pages ----------
      if (p === "/how-to") return new Response(page("how-to", HOWTO, user), { headers: { "Content-Type": "text/html" } });
      if (p === "/roost-signup") return new Response(page("get roost", SIGNUP, user), { headers: { "Content-Type": "text/html" } });

      // ---------- claim / login ----------
      if (p.startsWith("/claim/")) {
        const token = p.slice(7);
        const claim = await env.DB.prepare("SELECT username FROM claims WHERE token=?").bind(token).first();
        if (!claim) return new Response(page("invalid link", "<p>That login link isn't valid.</p>", null), { status: 404, headers: { "Content-Type": "text/html" } });
        await env.DB.prepare("INSERT OR IGNORE INTO users(username) VALUES (?)").bind(claim.username).run();
        const sess = crypto.randomUUID();
        await env.DB.prepare("INSERT INTO sessions(token, username) VALUES (?,?)").bind(sess, claim.username).run();
        return new Response(null, {
          status: 302,
          headers: {
            Location: "/",
            "Set-Cookie": `rs_session=${sess}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=31536000`,
          },
        });
      }

      // ---------- bot publish API ----------
      if (p === "/api/chirps" && req.method === "POST") {
        if (req.headers.get("X-Bot-Key") !== env.BOT_KEY) return new Response("forbidden", { status: 403 });
        const body = await req.json();
        const username = String(body.username || "").replace(/^@/, "").toLowerCase();
        if (!username) return new Response("username required", { status: 400 });
        const message = String(body.message || "");
        const hashtags = [...new Set([...(body.tags || []), ...[...message.matchAll(/#(\w+)/g)].map((m) => m[1].toLowerCase())])];
        const key = `chirps/${crypto.randomUUID()}.png`;
        const png = Uint8Array.from(atob(body.image_b64), (c) => c.charCodeAt(0));
        await env.ART.put(key, png, { httpMetadata: { contentType: "image/png" } });
        const ins = await env.DB.prepare("INSERT INTO chirps(username,message,image_key) VALUES (?,?,?) RETURNING id")
          .bind(username, message, key).first();
        for (const t of hashtags)
          await env.DB.prepare("INSERT OR IGNORE INTO chirp_tags(chirp_id,tag,added_by) VALUES (?,?,'bot')").bind(ins.id, t).run();
        let claim = await env.DB.prepare("SELECT token FROM claims WHERE username=?").bind(username).first();
        if (!claim) {
          claim = { token: crypto.randomUUID() };
          await env.DB.prepare("INSERT INTO claims(token,username) VALUES (?,?)").bind(claim.token, username).run();
        }
        return Response.json({ id: ins.id, url: `${url.origin}/chirp/${ins.id}`, claim_url: `${url.origin}/claim/${claim.token}` });
      }

      // ---------- rank / tag (logged-in only) ----------
      if ((p === "/api/rank" || p === "/api/tag") && req.method === "POST") {
        if (!user) return new Response(page("login required", `<p>Only logged-in flock members can do that. <a href="/how-to#login">How to log in</a>.</p>`, null), { status: 401, headers: { "Content-Type": "text/html" } });
        const form = await req.formData();
        const id = Number(form.get("chirp_id"));
        if (p === "/api/rank") {
          const score = Math.max(1, Math.min(10, Number(form.get("score"))));
          await env.DB.prepare("INSERT INTO ratings(chirp_id,username,score) VALUES (?,?,?) ON CONFLICT(chirp_id,username) DO UPDATE SET score=excluded.score")
            .bind(id, user, score).run();
        } else {
          const tag = String(form.get("tag") || "").toLowerCase().replace(/[^\w]/g, "").slice(0, 24);
          if (tag) await env.DB.prepare("INSERT OR IGNORE INTO chirp_tags(chirp_id,tag,added_by) VALUES (?,?,?)").bind(id, tag, user).run();
        }
        return Response.redirect(`${url.origin}/chirp/${id}`, 302);
      }

      // ---------- chirp detail ----------
      const detail = p.match(/^\/chirp\/(\d+)$/);
      if (detail) {
        const c = await env.DB.prepare(`${FEED_SQL} WHERE c.id=? GROUP BY c.id`).bind(detail[1]).first();
        if (!c) return new Response("not found", { status: 404 });
        const actions = user
          ? `<form class="inline" method="post" action="/api/rank"><input type="hidden" name="chirp_id" value="${c.id}">
               <label>rank</label><select name="score">${Array.from({ length: 10 }, (_, i) => `<option>${i + 1}</option>`).join("")}</select>
               <button>chirp it</button></form>
             <form class="inline" method="post" action="/api/tag"><input type="hidden" name="chirp_id" value="${c.id}">
               <input name="tag" placeholder="add a tag" maxlength="24"><button>tag</button></form>`
          : `<p class="meta">log in via your bird link to rank or tag — <a href="/how-to#login">how</a></p>`;
        return new Response(page(`chirp #${c.id}`, chirpCard(c, true) + actions, user), { headers: { "Content-Type": "text/html" } });
      }

      // ---------- feeds ----------
      let rows, heading;
      if (p === "/popular") {
        heading = "popular";
        rows = await env.DB.prepare(`${FEED_SQL} GROUP BY c.id HAVING votes>0 ORDER BY avg*MIN(votes,3) DESC, c.created_at DESC LIMIT 60`).all();
      } else if (p === "/search") {
        const q = (url.searchParams.get("q") || "").trim();
        heading = q ? `search: ${esc(q)}` : "search";
        if (!q) {
          return new Response(page("search", `<h2>search</h2><form class="inline" action="/search"><input class="search" name="q" placeholder="#tag, @username, or words"><button>search</button></form>`, user), { headers: { "Content-Type": "text/html" } });
        }
        let sql, bind;
        if (q.startsWith("#")) { sql = `${FEED_SQL} WHERE c.id IN (SELECT chirp_id FROM chirp_tags WHERE tag=?) GROUP BY c.id ORDER BY c.created_at DESC LIMIT 60`; bind = [q.slice(1).toLowerCase()]; }
        else if (q.startsWith("@")) { sql = `${FEED_SQL} WHERE c.username=? GROUP BY c.id ORDER BY c.created_at DESC LIMIT 60`; bind = [q.slice(1).toLowerCase()]; }
        else { sql = `${FEED_SQL} WHERE c.message LIKE ? OR c.username LIKE ? GROUP BY c.id ORDER BY c.created_at DESC LIMIT 60`; bind = [`%${q}%`, `%${q}%`]; }
        rows = await env.DB.prepare(sql).bind(...bind).all();
      } else {
        heading = "recent";
        rows = await env.DB.prepare(`${FEED_SQL} GROUP BY c.id ORDER BY c.created_at DESC LIMIT 60`).all();
      }
      const cards = (rows.results || []).map((c) => chirpCard(c)).join("") || `<p>No chirps yet — <a href="/how-to#publish">send the first one</a>.</p>`;
      const searchBox = p === "/search" ? `<form class="inline" action="/search"><input class="search" name="q" value="${esc(url.searchParams.get("q") || "")}"><button>search</button></form>` : "";
      return new Response(page(heading, `<h2>${heading}</h2>${searchBox}<div class="grid">${cards}</div>`, user), { headers: { "Content-Type": "text/html" } });
    } catch (e) {
      return new Response(`error: ${e.message}`, { status: 500 });
    }
  },
};
