# Roost Trace-Over-Image + RoostDraw Distribution — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship two independent capabilities — (A) a "load a reference image and trace over it" guide in the web viewer (and, deferred, native RoostDraw), and (B) a non–App-Store distribution pipeline that turns RoostDraw into a signed, user-deployable macOS app via GitHub Releases → Homebrew cask → npm.

**Architecture:** Phase A is purely additive front-end work on the self-contained `roost_sim/viewer.html` (a transient `state.trace` object that never enters `state.strokes`). Phase B wraps the existing SwiftPM `RoostDraw` binary into a signed `.app` bundle through a single `build-app.sh` (ad-hoc by default, Developer ID + notarization when credentials are present), then publishes it.

**Tech Stack:** Vanilla HTML/Canvas/JS (viewer); Swift 6 / SwiftPM, `codesign`, `xcrun notarytool`/`stapler`, `hdiutil`, Homebrew Cask Ruby, Node.js (distribution).

## Global Constraints

- **rpaint invariant:** the reference image MUST NOT enter any `strokes` entry. `sim.py normalize_strokes` raises `ValueError` on non-point data. The guide lives only in `state.trace` (web) / a non-serialized `AppState` field (native).
- **Canvas constants are fixed and identical across web/Python/Swift:** `CANVAS=530`, `THICK=14`, `THIN=5`, palette hexes `#111111/#ffffff/#d2413c/#4583d6/#5d9e58/#e7b63c`. Do not change.
- **`.rpaint.json` stays cross-tool compatible** (`sim.py`, `replay.py`, `viewer.html`, RoostDraw). Loaders read `data.strokes || data.drawing.strokes`; unknown sibling keys are ignored.
- **Signing path (user-confirmed):** Developer ID + notarization is the canonical target; ad-hoc `codesign -s -` is the zero-cost fallback the script must still support.
- **Names:** app `RoostDraw`; bundle id `art.roostsocial.RoostDraw`; repo `ashrocket/roost-draw`; tap `ashrocket/homebrew-roostdraw`.
- **Parity features (etch pen/grid/stats/title) are being implemented in parallel** by another agent in `controller/RoostDraw/Sources/RoostDraw/`. Do NOT edit those Swift sources for Phase A-native or Phase B until that agent reports done (shared `.build`, merge risk).
- **Commits:** this repo commits only when the user asks; when committing, branch first off the relevant repo (`roostsocial.art` for the web/docs, nested `controller/` for RoostDraw). Commit steps below are the logical grouping — gate them on user go-ahead.

---

## Phase A — Trace-over-image (web viewer `roost_sim/viewer.html`)

Source of truth: `docs/superpowers/specs/2026-06-22-roost-trace-image-design.md`. All line numbers below are from that spec's implementation map and shift as edits land — re-grep before each edit.

### Task A1: Trace state, DOM handles, and toolbar section

**Files:**
- Modify: `roost_sim/viewer.html` (CSS before `.hidden`; toolbar HTML before the `Files` section; `state` object; `el` map)

**Interfaces:**
- Produces: `state.trace = { image, visible, opacity, grayscale, invert, name }`; DOM ids `#traceInput #traceLoadBtn #traceToggleBtn #traceClearBtn #traceOpacity #traceGray #traceInvert`; `el.trace*` handles.

- [ ] **Step 1:** Add the `trace` object to the `state` literal:
```js
trace: { image: null, visible: true, opacity: 0.35, grayscale: false, invert: false, name: null },
```
- [ ] **Step 2:** Add a new `<section>` to the toolbar immediately before the `Files` section:
```html
<section class="panel">
  <h2>Trace</h2>
  <input id="traceInput" class="hidden" type="file" accept="image/*">
  <div class="file-grid">
    <button id="traceLoadBtn" title="Load a reference image to trace">Load image</button>
    <button id="traceToggleBtn" title="Show/hide trace, shortcut b">Hide</button>
    <button id="traceClearBtn" title="Remove the reference image">Clear</button>
  </div>
  <div class="slider-row">
    <label for="traceOpacity">Dim</label>
    <input id="traceOpacity" type="range" min="0" max="100" value="35">
    <span id="traceOpacityText">35%</span>
  </div>
  <div class="file-grid">
    <button id="traceGray" title="Grayscale the reference">Gray</button>
    <button id="traceInvert" title="Invert the reference">Invert</button>
  </div>
</section>
```
- [ ] **Step 3:** Add the seven element handles to the `el` map:
```js
traceInput: document.getElementById("traceInput"),
traceLoadBtn: document.getElementById("traceLoadBtn"),
traceToggleBtn: document.getElementById("traceToggleBtn"),
traceClearBtn: document.getElementById("traceClearBtn"),
traceOpacity: document.getElementById("traceOpacity"),
traceOpacityText: document.getElementById("traceOpacityText"),
traceGray: document.getElementById("traceGray"),
traceInvert: document.getElementById("traceInvert"),
```
- [ ] **Step 4 (verify):** Reload `http://localhost:8731/viewer.html`; the Trace section renders above Files with no console errors. Screenshot.

### Task A2: Render the reference beneath strokes

**Files:** Modify: `roost_sim/viewer.html` (new fns near `drawEtchCursor`; one call inside `drawAll`)

**Interfaces:** Consumes `state.trace`, `VIEW_SIZE`, `ctx`. Produces `drawTraceImage()`, `loadTraceImage(file)`.

- [ ] **Step 1:** Add `drawTraceImage()` and `loadTraceImage(file)` exactly as specified (spec lines 100–130).
- [ ] **Step 2:** In `drawAll()`, insert `drawTraceImage();` after the white `fillRect` and before the strokes loop.
- [ ] **Step 3 (verify):** In the page console, `loadTraceImage` via a temporary `fetch`→`File` of `/bicycle_couple_265.png`; confirm the dimmed image appears centered behind any strokes. Screenshot.

### Task A3: Wire controls, updateUi, and newDrawing

**Files:** Modify: `roost_sim/viewer.html` (listeners block; `updateUi`; `newDrawing`)

- [ ] **Step 1:** Listeners: `traceLoadBtn`→`traceInput.click()`; `traceInput change`→`loadTraceImage(files[0])` then reset value; `traceToggleBtn`→flip `state.trace.visible`, `drawAll`, `updateUi`; `traceClearBtn`→null `image`/`name`, `drawAll`, `updateUi`; `traceOpacity input`→set `opacity=value/100`, update label, `drawAll`; `traceGray`/`traceInvert`→toggle flag, `drawAll`, `updateUi`.
- [ ] **Step 2:** In `updateUi()`: `traceToggleBtn` text `Hide`/`Show` + `.active` when visible; `traceOpacityText` = `${round(opacity*100)}%`; `traceGray`/`traceInvert` `.active` reflect flags; disable toggle/clear/opacity/gray/invert when `!state.trace.image`.
- [ ] **Step 3:** In `newDrawing()`: also `state.trace.image = null; state.trace.name = null;`. Leave `clearDrawing()`/Shake untouched (keep reference for re-tracing).
- [ ] **Step 4 (verify):** Load image, drag opacity, toggle gray/invert, Hide/Show, Clear — all behave; New clears the reference, Clear-canvas keeps it.

### Task A4: Drag-drop, paste, and keyboard shortcuts

**Files:** Modify: `roost_sim/viewer.html` (canvas/window listeners; keydown handler)

- [ ] **Step 1:** `el.shell` `dragover`→`preventDefault`; `drop`→if first file is `image/*` call `loadTraceImage`, else fall through to existing `openFile`.
- [ ] **Step 2:** `window` `paste`→if a clipboard item is an image, `loadTraceImage(item.getAsFile())`.
- [ ] **Step 3:** In keydown (after the existing guards that ignore typing in inputs): `b`→toggle visibility; `[`→opacity −0.05; `]`→opacity +0.05 (clamp 0–1; update slider + label + `drawAll`).
- [ ] **Step 4 (verify):** Drag a PNG onto the canvas → loads as trace; copy an image and paste → loads; `b`/`[`/`]` work and do NOT fire while typing in the title field.

### Task A5: Prove no leakage into device artifacts

**Files:** Test only (no source change)

- [ ] **Step 1:** Load a reference, draw 2–3 strokes, Save `.rpaint.json` to `roost_sim/_trace_leak_test.rpaint.json`.
- [ ] **Step 2:** Run:
```bash
python3 -c "import sys; sys.path.insert(0,'roost_sim'); import sim; s=sim.load_rpaint('roost_sim/_trace_leak_test.rpaint.json'); print(len(s),'strokes; ok')"
```
Expected: prints the stroke count and `ok` (no `ValueError`), and `grep -c data:image roost_sim/_trace_leak_test.rpaint.json` returns `0`.
- [ ] **Step 3:** Export PNG; confirm the reference is absent from the exported image. Delete the temp file.

### Task A6 (DEFERRED — after parity agent finishes): native trace in RoostDraw

**Files:** Modify `controller/RoostDraw/Sources/RoostDraw/{AppState,DrawingCanvasView,ToolbarView}.swift`

- [ ] Add `@Published traceImage: NSImage?`, `traceOpacity=0.4`, `traceVisible=true` (transient; not stroke/undo/serialized).
- [ ] In `DrawingCanvasView` `Canvas` closure, draw the contain-fit image after the white fill and before strokes, at `traceOpacity`, inside the translated/scaled context.
- [ ] ToolbarView "Trace" section: load (`NSOpenPanel` image types), opacity slider, show/hide, clear; drag-drop + paste as niceties.
- [ ] Verify `swift build` exit 0 + `--selftest`; confirm `renderToPNG`/`saveStrokes` exclude the image.

---

## Phase B — RoostDraw distribution pipeline (`controller/RoostDraw`)

Source of truth: `docs/superpowers/specs/2026-06-22-roost-swift-app-design.md` §6. Run after the parity agent reports done.

### Task B1: `Info.plist` + `build-app.sh` (assemble + sign)

**Files:**
- Create: `controller/RoostDraw/Resources/Info.plist`
- Create: `controller/RoostDraw/build-app.sh` (chmod +x)

**Interfaces:** Produces `RoostDraw.app` in `controller/RoostDraw/dist/`. Ad-hoc by default; Developer ID when `DEVELOPER_ID` + notary profile env vars are set.

- [ ] **Step 1:** Write `Info.plist` with `CFBundleExecutable=RoostDraw`, `CFBundleIdentifier=art.roostsocial.RoostDraw`, `CFBundlePackageType=APPL`, `LSMinimumSystemVersion=15.0`, `NSHighResolutionCapable=YES`, `NSPrincipalClass=NSApplication`, `CFBundleShortVersionString=1.0`, `CFBundleName=RoostDraw`, `CFBundleIconFile=RoostDraw` (icns optional in B2).
- [ ] **Step 2:** Write `build-app.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
APP=dist/RoostDraw.app
rm -rf dist && mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
swift build -c release
cp .build/release/RoostDraw "$APP/Contents/MacOS/RoostDraw"
cp Resources/Info.plist "$APP/Contents/Info.plist"
[ -f Resources/RoostDraw.icns ] && cp Resources/RoostDraw.icns "$APP/Contents/Resources/"
if [ -n "${DEVELOPER_ID:-}" ]; then
  codesign --force --options runtime --timestamp --sign "$DEVELOPER_ID" "$APP"
  echo "signed with Developer ID: $DEVELOPER_ID"
else
  codesign --force --deep --sign - "$APP"
  echo "ad-hoc signed (set DEVELOPER_ID=… to sign for distribution)"
fi
codesign --verify --strict --verbose=2 "$APP"
echo "built $APP"
```
- [ ] **Step 3 (verify):** `bash controller/RoostDraw/build-app.sh` → exits 0, prints `built …RoostDraw.app`, `codesign --verify` passes. `open controller/RoostDraw/dist/RoostDraw.app` launches the GUI (manual check) — this is the first real "signed mac app the user can run", satisfying the project goal in ad-hoc form.

### Task B2: App icon (`RoostDraw.icns`)

**Files:** Create: `controller/RoostDraw/Resources/RoostDraw.icns`

- [ ] **Step 1:** Generate a simple icon from the selftest/bicycle art (or a roost glyph): build a 1024² PNG, `iconutil -c icns` from an `.iconset`. Until then `build-app.sh` already no-ops the missing file.
- [ ] **Step 2 (verify):** Rebuild; Finder shows the icon on `RoostDraw.app`.

### Task B3: Developer ID notarization + staple (gated on Team ID)

**Files:** Create: `controller/RoostDraw/notarize.sh`

- [ ] **Step 1:** Script per spec §6.2: `ditto -c -k --keepParent dist/RoostDraw.app dist/RoostDraw.zip`; `xcrun notarytool submit … --keychain-profile roostdraw-notary --wait`; `xcrun stapler staple dist/RoostDraw.app`. Document the one-time `notarytool store-credentials` step at the top as a comment (needs the user's Apple ID, Team ID, app-specific password — the user runs this; never store secrets in the repo).
- [ ] **Step 2 (verify, requires user's Team ID):** after `DEVELOPER_ID=… build-app.sh && notarize.sh`, `xcrun stapler validate dist/RoostDraw.app` passes and `spctl -a -vv dist/RoostDraw.app` reports `accepted, source=Notarized Developer ID`.

### Task B4: `.dmg` packaging

**Files:** Modify: `controller/RoostDraw/build-app.sh` (add optional `--dmg`) or new `make-dmg.sh`

- [ ] **Step 1:** `hdiutil create -volname RoostDraw -srcfolder dist/RoostDraw.app -ov -format UDZO dist/RoostDraw-$VERSION.dmg`; if notarized, `xcrun stapler staple` the dmg.
- [ ] **Step 2 (verify):** `dist/RoostDraw-<v>.dmg` mounts and contains `RoostDraw.app`.

### Task B5: Homebrew cask + tap

**Files:** Create: `controller/homebrew-roostdraw/Casks/roostdraw.rb`

- [ ] **Step 1:** Write the cask exactly per spec §6.4 (version, `sha256` of the dmg, release URL, `depends_on macos: ">= :sequoia"`, `app "RoostDraw.app"`, `zap` the prefs plist).
- [ ] **Step 2 (verify):** `brew style --cask controller/homebrew-roostdraw/Casks/roostdraw.rb` passes; install flow documented (`brew tap ashrocket/roostdraw && brew install --cask roostdraw`) — live test deferred until a real GitHub release exists.

### Task B6: npm convenience fetcher

**Files:** Create: `controller/roostdraw-npm/{package.json, bin/roostdraw.js, scripts/fetch.js}`

- [ ] **Step 1:** `package.json` per spec §6.5 (`bin.roostdraw`, `os:["darwin"]`, `postinstall`).
- [ ] **Step 2:** `scripts/fetch.js` downloads the release `.zip`, verifies a pinned `sha256`, unzips the `.app` into the package. `bin/roostdraw.js` execs `open -a` the unpacked app.
- [ ] **Step 3 (verify):** `node scripts/fetch.js` against a real release asset unpacks a runnable `RoostDraw.app`; `npx roostdraw` opens it. Deferred until a release exists.

---

## Self-Review

- **Spec coverage:** Trace spec §data-model/§UX/§render/§implementation-map/§testing → Tasks A1–A5; native note → A6. Swift spec §6.0–6.6 → Tasks B1–B6; §0 rename → already done; §1 parity → parallel agent (out of scope here). ✔
- **Sequencing:** Phase A (web) has zero dependency on the parity agent and can start now. A6 + all of Phase B touch RoostDraw and wait for the parity agent. ✔
- **No secrets in repo:** notarization credentials are user-run via `notarytool store-credentials`; scripts read them from the keychain profile, never the tree. ✔
- **Goal linkage:** Task B1/B3 produce the signed, user-deployable `.app` that fulfills the project goal (ad-hoc immediately; notarized once Team ID is supplied). ✔
