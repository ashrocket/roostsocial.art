/**
 * roostsocial.art — gallery for Roost scratchpad art ("chirps").
 *
 * Feeds: / (recent), /popular, /search?q=
 * Submissions: ONLY via the Roost app — send your scratchpad by bird to
 *   @ashrocket. The publish bot posts it and a return bird brings your
 *   unique login code.
 * Auth: enter your code at /login (or follow a /claim link). Usernames are
 *   locked to Roost handles. Logged-in users rank (1-10) and tag chirps.
 * Bot:  POST /api/chirps with X-Bot-Key → publishes, returns code+claim URL.
 */

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const PALETTE = { bg: "#0e1116", card: "#1a212b", ink: "#e8edf4", dim: "#93a1b3", gold: "#e7b63c", blue: "#4583d6" };

const MADE_WITH = {
  ios: "📱 iOS",
  macos: "💻 macOS",
  pigeonpaint: "🎨 Pigeon Paint",
};

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
  .badge{display:inline-block;background:#243043;border-radius:6px;padding:.05rem .45rem;font-size:.78rem;color:${PALETTE.dim}}
  .score{color:${PALETTE.gold};font-weight:600}
  form.inline{display:inline-flex;gap:.4rem;align-items:center;margin-top:.5rem;flex-wrap:wrap}
  input,select,button{font:inherit;background:#243043;color:${PALETTE.ink};border:1px solid #34425a;border-radius:8px;padding:.25rem .6rem}
  button{background:${PALETTE.gold};color:#1a1409;border:none;cursor:pointer;font-weight:600}
  footer{border-top:1px solid #2a3340;margin-top:2rem;padding:1.2rem;color:${PALETTE.dim};font-size:.85rem;text-align:center}
  .search{width:min(420px,90%)}
  .notice{background:#243043;border-radius:10px;padding:.7rem 1rem;margin:.8rem 0}
</style></head><body>
<header>
  <h1><a href="/">🕊️ roostsocial.art</a></h1>
  <nav><a href="/">recent</a> <a href="/popular">popular</a> <a href="/search">search</a> <a href="/how-to">how-to</a></nav>
  <span class="who">${user ? `<a href="/account">@${esc(user)}</a>` : `<a href="/login">log in</a>`}</span>
</header>
<main>${body}</main>
<footer>
  <p><b>Get Roost</b>: <a href="/roost-signup">sign up for the Roost app</a> ·
  <a href="/how-to#art">how to make scratchpad art</a> ·
  <a href="/how-to#publish">submit art (Roost app only)</a> ·
  <b>Pigeon Paint</b>: <a href="https://github.com/ashrocket/pigeon-paint">source</a> / <a href="/controller.zip">download</a> —
  <a href="/how-to#pigeonpaint">MS&nbsp;Paint-style control of the scratchpad</a></p>
  <p>art arrives by carrier pigeon · ranks are 1–10 chirps · tags welcome</p>
</footer>
</body></html>`;
}

function chirpCard(c, detail = false) {
  const tags = (c.tags || "").split(",").filter(Boolean)
    .map((t) => `<a href="/search?q=%23${encodeURIComponent(t)}">#${esc(t)}</a>`).join(" ");
  const score = c.votes ? `<span class="score">${Number(c.avg).toFixed(1)}/10</span> · ${c.votes} chirp${c.votes == 1 ? "" : "s"}` : "unranked";
  const made = MADE_WITH[c.created_with] ? ` · <span class="badge">${MADE_WITH[c.created_with]}</span>` : "";
  return `<div class="chirp">
    ${detail ? "" : `<a href="/chirp/${c.id}">`}<img src="/img/${esc(c.image_key)}" alt="scratchpad art by @${esc(c.username)}">${detail ? "" : "</a>"}
    ${c.message ? `<div class="msg">${esc(c.message)}</div>` : ""}
    <div class="tags">${tags}</div>
    <div class="meta">by <a href="/search?q=%40${encodeURIComponent(c.username)}">@${esc(c.username)}</a> · ${esc((c.created_at || "").slice(0, 16))} · ${score}${made}</div>
  </div>`;
}

const FEED_SQL = `
  SELECT c.*, COALESCE(AVG(r.score),0) avg, COUNT(r.score) votes,
    (SELECT GROUP_CONCAT(DISTINCT tag) FROM chirp_tags t WHERE t.chirp_id=c.id) tags
  FROM chirps c LEFT JOIN ratings r ON r.chirp_id=c.id
  WHERE c.status='live'`;

// Detail pages need the chirp regardless of status (to show the removed notice).
const FEED_SQL_ANY = FEED_SQL.replace("WHERE c.status='live'", "WHERE 1=1");

async function getUser(req, env) {
  const cookie = req.headers.get("Cookie") || "";
  const m = cookie.match(/rs_session=([A-Za-z0-9-]+)/);
  if (!m) return null;
  const row = await env.DB.prepare("SELECT username FROM sessions WHERE token=?").bind(m[1]).first();
  return row ? row.username : null;
}

async function startSession(env, username) {
  await env.DB.prepare("INSERT OR IGNORE INTO users(username) VALUES (?)").bind(username).run();
  const sess = crypto.randomUUID();
  await env.DB.prepare("INSERT INTO sessions(token, username) VALUES (?,?)").bind(sess, username).run();
  return {
    status: 302,
    headers: {
      Location: "/account",
      "Set-Cookie": `rs_session=${sess}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=31536000`,
    },
  };
}

function newCode() {
  // 6-char unambiguous code, e.g. R7K2MD
  const alphabet = "ABCDEFGHJKMNPQRSTVWXYZ23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(6));
  return [...bytes].map((b) => alphabet[b % alphabet.length]).join("");
}

const HOWTO = `
<h2>How roostsocial.art works</h2>
<p class="notice"><b>All submissions are by Roost app only.</b> There is no upload form, no email inbox, no API for art.
If it didn't fly here on a bird, it doesn't get published.</p>
<p id="art"><b>1. Make art in Roost.</b> Open any message and tap <i>+ → Scratchpad</i>.
Draw with the six-color pen — it is speed-sensitive: fast strokes are thick, slow strokes are thin.</p>
<p id="publish"><b>2. Send it to the publish bot.</b> Send your scratchpad by bird to <b>@ashrocket</b>.
Text in the same message is published with it, and any <b>#hashtags</b> become tags.</p>
<p id="login"><b>3. Get your login code.</b> A return bird brings a unique code for your account
(names are locked to Roost usernames). Enter it at <a href="/login">/login</a> — that's it, you're in:
rank any chirp 1–10 and add tags.</p>
<p id="email"><b>4. Optional: magic-link email login.</b> Once logged in, add your email on
<a href="/account">your account page</a>. We'll send a verification code to your email — send that code
back to @ashrocket <i>by bird</i> to prove the email belongs to your roost. After that, magic links replace codes.
<span class="badge">email verification is being wired up — codes work today</span></p>
<p id="pigeonpaint"><b>5. Pro tools: Pigeon Paint.</b> Drawing with a trackpad is hard. The open-source
<a href="https://github.com/ashrocket/pigeon-paint">Pigeon Paint</a> controller (<a href="/controller.zip">direct download</a>)
gives you MS&nbsp;Paint-style tools — lines, rectangles, ellipses, eraser, undo, the exact Roost palette — and replays
your drawing onto the real scratchpad with precise synthetic strokes. <code>python3 roostpaint.py</code> on macOS.
The secret to drawing well on the scratchpad is using the macOS app instead of the iOS app.</p>
<p>Every chirp can carry a badge for how it was made: 📱 iOS · 💻 macOS · 🎨 Pigeon Paint.</p>
<p id="signup"><b>Get Roost:</b> Roost is in beta — <a href="/roost-signup">sign-up details here</a>.</p>`;

const SIGNUP = `
<h2>Get the Roost app</h2>
<p>Roost is a carrier-pigeon messaging app — your messages travel as birds, in real time, across a real map.</p>
<p>It is currently in invite-only beta. Ask <b>@ashrocket</b> for a TestFlight invite
(send a bird, or failing that, an email). When the public TestFlight link lands it will live right here.</p>
<p>Once you're in: <a href="/how-to">here's how to make and publish scratchpad art</a>.</p>`;

const LOGIN = (err) => `
<h2>log in</h2>
${err ? `<p class="notice">${esc(err)}</p>` : ""}
<p>Enter the code a bird brought you. No bird yet? <a href="/how-to#publish">Send art to @ashrocket</a> and one will fly back.</p>
<form class="inline" method="post" action="/login">
  <input name="code" placeholder="e.g. R7K2MD" maxlength="12" style="text-transform:uppercase">
  <button>enter the roost</button>
</form>`;

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
        if (!obj) return new Response("Pigeon Paint build not uploaded yet — check back soon", { status: 404 });
        return new Response(obj.body, { headers: { "Content-Type": "application/zip", "Content-Disposition": 'attachment; filename="pigeon-paint.zip"' } });
      }

      // ---------- static-ish pages ----------
      if (p === "/how-to") return new Response(page("how-to", HOWTO, user), { headers: { "Content-Type": "text/html" } });
      if (p === "/roost-signup") return new Response(page("get roost", SIGNUP, user), { headers: { "Content-Type": "text/html" } });

      // ---------- code login ----------
      if (p === "/login" && req.method === "GET")
        return new Response(page("log in", LOGIN(), user), { headers: { "Content-Type": "text/html" } });
      if (p === "/login" && req.method === "POST") {
        const form = await req.formData();
        const code = String(form.get("code") || "").trim().toUpperCase();
        const row = code && await env.DB.prepare("SELECT username FROM login_codes WHERE code=?").bind(code).first();
        if (!row) return new Response(page("log in", LOGIN("That code doesn't match any roost. Check the bird's message and try again."), user), { status: 401, headers: { "Content-Type": "text/html" } });
        const sess = await startSession(env, row.username);
        return new Response(null, sess);
      }

      // ---------- claim / login link (legacy + convenience) ----------
      if (p.startsWith("/claim/")) {
        const token = p.slice(7);
        const claim = await env.DB.prepare("SELECT username FROM claims WHERE token=?").bind(token).first();
        if (!claim) return new Response(page("invalid link", "<p>That login link isn't valid.</p>", null), { status: 404, headers: { "Content-Type": "text/html" } });
        const sess = await startSession(env, claim.username);
        return new Response(null, sess);
      }

      // ---------- account ----------
      if (p === "/account") {
        if (!user) return Response.redirect(`${url.origin}/login`, 302);
        const ev = await env.DB.prepare("SELECT email, verified FROM email_verifications WHERE username=?").bind(user).first();
        const emailBlock = ev?.verified
          ? `<p>✅ <b>${esc(ev.email)}</b> is verified — magic-link login is on.</p>`
          : ev?.email
            ? `<p>⏳ <b>${esc(ev.email)}</b> is pending: a verification code is on its way to your email.
               Send that code back to <b>@ashrocket</b> by bird to finish linking it to your roost.</p>`
            : "";
        const body = `<h2>@${esc(user)}'s roost</h2>
          <p>You can rank chirps 1–10 and add tags anywhere on the site.</p>
          ${emailBlock}
          <form class="inline" method="post" action="/api/email">
            <input name="email" type="email" placeholder="you@example.com" required>
            <button>${ev?.email ? "change email" : "add email for magic-link login"}</button>
          </form>
          <p class="meta">Email login is being wired up — your code keeps working either way.</p>`;
        return new Response(page("account", body, user), { headers: { "Content-Type": "text/html" } });
      }
      if (p === "/api/email" && req.method === "POST") {
        if (!user) return Response.redirect(`${url.origin}/login`, 302);
        const form = await req.formData();
        const email = String(form.get("email") || "").slice(0, 200);
        const vcode = newCode();
        await env.DB.prepare(`INSERT INTO email_verifications(username,email,verified,code) VALUES (?,?,0,?)
          ON CONFLICT(username) DO UPDATE SET email=excluded.email, verified=0, code=excluded.code`)
          .bind(user, email, vcode).run();
        return Response.redirect(`${url.origin}/account`, 302);
      }

      // ---------- bot publish API ----------
      if (p === "/api/chirps" && req.method === "POST") {
        if (req.headers.get("X-Bot-Key") !== env.BOT_KEY) return new Response("forbidden", { status: 403 });
        const body = await req.json();
        const username = String(body.username || "").replace(/^@/, "").toLowerCase();
        if (!username) return new Response("username required", { status: 400 });
        const message = String(body.message || "");
        const createdWith = ["ios", "macos", "pigeonpaint"].includes(body.created_with) ? body.created_with : "";
        const hashtags = [...new Set([...(body.tags || []), ...[...message.matchAll(/#(\w+)/g)].map((m) => m[1].toLowerCase())])];
        const key = `chirps/${crypto.randomUUID()}.png`;
        const png = Uint8Array.from(atob(body.image_b64), (c) => c.charCodeAt(0));
        await env.ART.put(key, png, { httpMetadata: { contentType: "image/png" } });
        const ins = await env.DB.prepare("INSERT INTO chirps(username,message,image_key,created_with) VALUES (?,?,?,?) RETURNING id")
          .bind(username, message, key, createdWith).first();
        for (const t of hashtags)
          await env.DB.prepare("INSERT OR IGNORE INTO chirp_tags(chirp_id,tag,added_by) VALUES (?,?,'bot')").bind(ins.id, t).run();
        let codeRow = await env.DB.prepare("SELECT code FROM login_codes WHERE username=?").bind(username).first();
        if (!codeRow) {
          codeRow = { code: newCode() };
          await env.DB.prepare("INSERT INTO login_codes(code,username) VALUES (?,?)").bind(codeRow.code, username).run();
        }
        let claim = await env.DB.prepare("SELECT token FROM claims WHERE username=?").bind(username).first();
        if (!claim) {
          claim = { token: crypto.randomUUID() };
          await env.DB.prepare("INSERT INTO claims(token,username) VALUES (?,?)").bind(claim.token, username).run();
        }
        return Response.json({
          id: ins.id,
          url: `${url.origin}/chirp/${ins.id}`,
          code: codeRow.code,
          claim_url: `${url.origin}/claim/${claim.token}`,
        });
      }

      // ---------- rank / tag (logged-in only) ----------
      if ((p === "/api/rank" || p === "/api/tag") && req.method === "POST") {
        if (!user) return new Response(page("login required", `<p>Only logged-in flock members can do that. <a href="/login">Enter your code</a> or <a href="/how-to#login">get one</a>.</p>`, null), { status: 401, headers: { "Content-Type": "text/html" } });
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

      // ---------- art removal requests ----------
      if (p === "/api/takedown" && req.method === "POST") {
        if (!user) return new Response(page("login required", `<p>Only logged-in flock members can do that. <a href="/login">Enter your code</a> or <a href="/how-to#login">get one</a>.</p>`, null), { status: 401, headers: { "Content-Type": "text/html" } });
        const form = await req.formData();
        const id = Number(form.get("chirp_id"));
        const note = String(form.get("note") || "").slice(0, 300);
        const c = await env.DB.prepare("SELECT id, username, status FROM chirps WHERE id=?").bind(id).first();
        if (!c) return new Response("not found", { status: 404 });
        if (user === c.username) {
          // The artist always wins: immediate removal, no review step.
          await env.DB.prepare("UPDATE chirps SET status='removed' WHERE id=?").bind(id).run();
          await env.DB.prepare("INSERT INTO takedowns(chirp_id,requester,reason,note,status) VALUES (?,?,'owner',?,'done')").bind(id, user, note).run();
        } else if (c.status === "live") {
          // Offense reports hide the art until Ashley reviews the request.
          await env.DB.prepare("UPDATE chirps SET status='flagged' WHERE id=?").bind(id).run();
          await env.DB.prepare("INSERT INTO takedowns(chirp_id,requester,reason,note,status) VALUES (?,?,'offensive',?,'pending')").bind(id, user, note).run();
        }
        return Response.redirect(`${url.origin}/chirp/${id}`, 302);
      }

      // ---------- moderation (bot key) ----------
      if (p === "/api/mod/takedowns" && req.method === "GET") {
        if (req.headers.get("X-Bot-Key") !== env.BOT_KEY) return new Response("forbidden", { status: 403 });
        const rows = await env.DB.prepare("SELECT t.*, c.username artist, c.image_key FROM takedowns t JOIN chirps c ON c.id=t.chirp_id WHERE t.status='pending' ORDER BY t.created_at").all();
        return Response.json(rows.results || []);
      }
      const modAct = p.match(/^\/api\/mod\/takedowns\/(\d+)$/);
      if (modAct && req.method === "POST") {
        if (req.headers.get("X-Bot-Key") !== env.BOT_KEY) return new Response("forbidden", { status: 403 });
        const act = (await req.json().catch(() => ({}))).action;
        const t = await env.DB.prepare("SELECT * FROM takedowns WHERE id=?").bind(modAct[1]).first();
        if (!t) return new Response("not found", { status: 404 });
        if (act === "restore") {
          await env.DB.prepare("UPDATE chirps SET status='live' WHERE id=?").bind(t.chirp_id).run();
          await env.DB.prepare("UPDATE takedowns SET status='dismissed' WHERE id=?").bind(t.id).run();
        } else {
          await env.DB.prepare("UPDATE chirps SET status='removed' WHERE id=?").bind(t.chirp_id).run();
          await env.DB.prepare("UPDATE takedowns SET status='done' WHERE id=?").bind(t.id).run();
        }
        return Response.json({ ok: true });
      }

      // ---------- chirp detail ----------
      const detail = p.match(/^\/chirp\/(\d+)$/);
      if (detail) {
        const c = await env.DB.prepare(`${FEED_SQL_ANY} AND c.id=? GROUP BY c.id`).bind(detail[1]).first();
        if (!c) return new Response("not found", { status: 404 });
        if (c.status !== "live") {
          const note = c.status === "flagged"
            ? "This chirp is hidden while a removal request is reviewed."
            : "This chirp was removed" + (c.status === "removed" ? "." : " by the artist.");
          return new Response(page(`chirp #${c.id}`, `<p class="notice">${note}</p>`, user), { status: 410, headers: { "Content-Type": "text/html" } });
        }
        const takedownForm = user
          ? user === c.username
            ? `<form class="inline" method="post" action="/api/takedown"><input type="hidden" name="chirp_id" value="${c.id}">
                 <button>remove my artwork</button></form>`
            : `<form class="inline" method="post" action="/api/takedown"><input type="hidden" name="chirp_id" value="${c.id}">
                 <input name="note" placeholder="why is this offensive? (optional)" maxlength="300"><button>report as offensive</button></form>`
          : "";
        const actions = user
          ? `<form class="inline" method="post" action="/api/rank"><input type="hidden" name="chirp_id" value="${c.id}">
               <label>rank</label><select name="score">${Array.from({ length: 10 }, (_, i) => `<option>${i + 1}</option>`).join("")}</select>
               <button>chirp it</button></form>
             <form class="inline" method="post" action="/api/tag"><input type="hidden" name="chirp_id" value="${c.id}">
               <input name="tag" placeholder="add a tag" maxlength="24"><button>tag</button></form>`
          : `<p class="meta"><a href="/login">log in with your code</a> to rank or tag — <a href="/how-to#login">how</a></p>`;
        return new Response(page(`chirp #${c.id}`, chirpCard(c, true) + actions + takedownForm, user), { headers: { "Content-Type": "text/html" } });
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
        if (q.startsWith("#")) { sql = `${FEED_SQL} AND c.id IN (SELECT chirp_id FROM chirp_tags WHERE tag=?) GROUP BY c.id ORDER BY c.created_at DESC LIMIT 60`; bind = [q.slice(1).toLowerCase()]; }
        else if (q.startsWith("@")) { sql = `${FEED_SQL} AND c.username=? GROUP BY c.id ORDER BY c.created_at DESC LIMIT 60`; bind = [q.slice(1).toLowerCase()]; }
        else { sql = `${FEED_SQL} AND (c.message LIKE ? OR c.username LIKE ?) GROUP BY c.id ORDER BY c.created_at DESC LIMIT 60`; bind = [`%${q}%`, `%${q}%`]; }
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
