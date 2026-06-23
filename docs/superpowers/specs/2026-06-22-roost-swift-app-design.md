# RoostDraw — Native macOS App Design (non–App Store distribution)

**Date:** 2026-06-22
**Status:** Design doc (no code, no commits)
**Scope:** Turn the Roost scratchpad tool into a native macOS Swift app named **RoostDraw**, built and deployed by the user *outside* the Mac App Store (Developer ID + notarization, or ad-hoc/self-signed fallback), shipped through three complementary channels: a signed `.app` on GitHub Releases, a Homebrew cask, and a thin npm fetcher.

> **Key finding:** this is not a green-field port. A working SwiftPM app already exists at `controller/PigeonPaint` (to be renamed **RoostDraw**). It **builds clean** (`swift build` → exit 0, Swift 6.3.1 / macOS 26 arm64) and **runs headless** (`--selftest` and `--export` CLI paths verified). It is roughly **~60% feature-parity** with the browser tool, and its `.rpaint.json` output is already consumed by `controller/replay.py` and round-trips with `roost_sim/sim.py`.

---

## Open decisions for the user

1. **Apple Developer Program membership + Team ID?** This is the gate. *Yes* → Developer ID signing + notarization + stapling → frictionless `.dmg`, Homebrew cask, and npm install. *No* → ad-hoc/self-signed only (works great locally and via npm fetch; browser-downloaded `.dmg`/`.zip` hit a one-time Gatekeeper prompt). What is the Team ID?
2. **Bundle identifier?** Proposed `art.roostsocial.RoostDraw` (reverse-DNS of roostsocial.art). Confirm — it threads through notarization, the cask `zap` stanza, and prefs.
3. **Which channel(s) to prioritize first?** Recommended order: GitHub Release (`.dmg`/`.zip`) → Homebrew cask → npm. Confirm or reorder.
4. **GitHub repo + tap rename.** Current source URL is `github.com/ashrocket/pigeon-paint`. Proposed: repo → `ashrocket/roost-draw`, Homebrew tap → `ashrocket/homebrew-roostdraw`. Confirm names.
5. **Parity scope for the native app.** Bring the missing web features (etch pen model, execution-manual `.md` export, grid, live stats, editable title) to RoostDraw, or keep it a focused MacPaint-style editor? Note: `replay.py` already drives the device from RoostDraw's `.rpaint.json`, so execution-manual export is *optional*, not required.
6. **Packaging tooling.** Stay on SwiftPM + a `build-app.sh` wrapper (recommended, lightweight), or migrate to an `.xcodeproj` for built-in signing/notarization/app-icon ergonomics?

**Assumptions made** (flag if wrong): macOS 15+ deployment target (Package.swift declares `.macOS(.v15)`); Apple Silicon primary, universal binary optional; user typically builds locally (no quarantine) for personal use, so signing matters mainly for *redistribution*; non-sandboxed app (needs arbitrary open/save), which is fine and notarizable for non–App Store; the sibling web trace-image feature is specced separately at `docs/superpowers/specs/2026-06-22-roost-trace-image-design.md`.

---

## 1. Current state assessment (`controller/PigeonPaint` → RoostDraw)

**Stack:** SwiftPM executable, `swift-tools-version: 6.0`, `platforms: [.macOS(.v15)]`. **SwiftUI** for UI with **AppKit** bridged where needed (NSApplicationDelegateAdaptor, NSOpenPanel/NSSavePanel/NSAlert, NSEvent scroll monitor, CoreGraphics PNG export). Clean separation; no third-party dependencies.

**Source map (`Sources/PigeonPaint/`):**

| File | Responsibility |
|---|---|
| `main.swift` | Entry point. Intercepts CLI modes `--selftest` (writes `selftest.png`) and `--export <file.rpaint.json>` (headless PNG) before launching the GUI via `PigeonPaintApp.main()`. |
| `PigeonPaintApp.swift` | SwiftUI `App` + `ContentView` (HStack: ToolbarView \| Divider \| DrawingCanvasView). `.commands` wires File (New/Open/Save/Save As/Export PNG) and Edit (Undo/Redo/Clear) menus with shortcuts. |
| `AppState.swift` | `ObservableObject` model: strokes, grouped undo/redo, tool/color/mode/fill, live-drawing lifecycle, file I/O (open/save/saveAs/exportPNG) with dirty-tracking, recent-docs, and unsaved-changes alerts. |
| `StrokeModel.swift` | `PaintColor` (6 colors, hex matches sim.py), `Stroke` (id/color/mode/normalized points), `.rpaint.json` load/save, NSColor hex helper. |
| `Geometry.swift` | Constants (`CANVAS_SIZE=530`, `THICK_PX=14`, `THIN_PX=5`), `DrawingTool` enum, scribble-fill (rect/ellipse), ellipse polygon, shift-constraint, `normalize()`. |
| `DrawingCanvasView.swift` | SwiftUI `Canvas` renderer + viewport (pan/zoom 0.25–8×), NSEvent scroll/zoom bridge, magnification gesture, combined draw/pan drag (Option = pan), key shortcuts (p/l/r/o/e/f, =/+/−/0). |
| `ToolbarView.swift` | Tool buttons, thick/thin, fill toggle, palette, undo/redo, scroll-sensitivity slider. |
| `Render.swift` | Headless CoreGraphics PNG export (2× retina) + selftest stroke set. |
| `AppDelegate.swift` | Quit/close interception → save-before-quit prompt. |

**Build status:** `swift build` → `Build complete!`, exit 0. No warnings surfaced.
**Run status:** `./.build/debug/PigeonPaint --selftest` → `selftest.png written — 57 strokes` (44 KB). `--export ../lincoln_pool.rpaint.json` → `exported lincoln_pool.png`. GUI not launched here (needs a window server; would block headless) but the SwiftUI scene is standard and the AppDelegate is wired.

**Strengths over the web tool:** native Open/Save panels, recent documents, unsaved-changes prompts, document proxy icon, smooth pan + pinch-zoom + scroll-sensitivity, and headless CLI (`--selftest`, `--export`) for CI/scripting.

---

## 2. Format interoperability (verified)

- **`.rpaint.json`** is the lingua franca across web (`viewer.html`), Python (`sim.py`), and Swift. `sim.py` writes a rich envelope `{version, format, title, palette, canvas, strokes:[[color,mode,[[u,v]…]]]}`; loaders only require `strokes`. PigeonPaint's `saveStrokes` writes a **subset** `{version, strokes}` (sorted keys) and `loadStrokes` reads only `strokes`, tolerating unknown color/mode (falls back to black/thick). **Round-trip works both directions**; the only drift is that PigeonPaint **drops `title`/`palette`/`canvas`/`format` on save**.
  - *Recommendation:* have RoostDraw emit the full sim.py envelope (add `format:"roost-rpaint"`, `title`, `palette`, `canvas`) so files stay self-describing. Pairs with adding an editable title (see §4).
- **Constants match** everywhere: canvas 530, thick 14 / thin 5, palette hexes (`#111111/#ffffff/#d2413c/#4583d6/#5d9e58/#e7b63c`). No normalization drift.
- **Device replay:** `controller/replay.py` reads `.rpaint.json` straight from `~/.roost/drawings/` and drives the real Roost scratchpad. RoostDraw's saves are therefore **already replay-ready** — no execution-manual needed for the device path. (The execution-manual `.md` from `sim.py` targets computer-use automation specifically; it's a separable artifact.)

---

## 3. Gap analysis vs the browser tool (`viewer.html`)

| Feature | Web tool | PigeonPaint/RoostDraw | Notes |
|---|---|---|---|
| Pencil / Line / Rect / Oval / Eraser | ✅ | ✅ | `ellipse` = oval. Eraser = white thick. |
| Fill (rect/oval) | ✅ | ✅ | Both use scribble-fill (replay-safe thin lines). |
| 6-color palette | ✅ | ✅ | Hexes identical. |
| Thick / Thin | ✅ | ✅ | 14/5 px. |
| Undo / Redo / Clear | ✅ | ✅ | RoostDraw groups undo by logical action. |
| Zoom / Pan | ✅ (±/100%) | ✅ **(better)** | Pan, pinch, fit, sensitivity — but **no on-screen zoom-% readout**. |
| Load / Save `.rpaint.json` | ✅ | ✅ | Subset envelope on save (see §2). |
| Export PNG | ✅ | ✅ | RoostDraw 2× retina. |
| **Grid toggle** | ✅ | ❌ | Missing. |
| **Etch pen model** (X/Y dials, nudge, pen up/down, shake) | ✅ | ❌ | Entirely missing — the biggest sim feature gap. |
| **Editable title field** | ✅ | ⚠️ partial | Window shows filename + dirty dot; no in-canvas editable title, not written to JSON. |
| **Live stats** (strokes/actions/tool/mode) | ✅ | ❌ | Missing. |
| **Execution-manual `.md` export + live preview** | ✅ | ❌ | Missing; optional for device replay (§2). |
| Native file panels / recents / dirty prompts | ❌ | ✅ | RoostDraw advantage. |

**Parity ≈ 60%** of the web feature set, with stronger native file/navigation UX. Missing, in rough priority: editable title + full JSON envelope (cheap, improves interop) → grid (cheap) → live stats (cheap) → execution-manual export (medium, optional) → etch pen model (largest; pure simulation nicety).

---

## 4. Implementation roadmap

### Step 0 — Rename PigeonPaint → RoostDraw *(first task; coordinator will do the physical move)*
Run inside the `controller/` git repo:
```bash
git mv controller/PigeonPaint controller/RoostDraw
git mv controller/RoostDraw/Sources/PigeonPaint controller/RoostDraw/Sources/RoostDraw
```
Then:
- **`Package.swift`** — `name: "RoostDraw"`, `.executableTarget(name: "RoostDraw", path: "Sources/RoostDraw")`.
- **Rename `PigeonPaintApp` → `RoostDrawApp`** (file `RoostDrawApp.swift`); update the `PigeonPaintApp.main()` call in `main.swift`.
- **README + source URL:** `github.com/ashrocket/pigeon-paint` → `github.com/ashrocket/roost-draw`; product name "Roost Paint"/"Pigeon Paint" → **RoostDraw**.
- Binary path becomes `.build/debug/RoostDraw`; update `--selftest`/`--export` docs. `.build/` rebuilds automatically.
- Adopt bundle id `art.roostsocial.RoostDraw`.

### Step 1 — Interop polish (cheap, high value)
Emit full sim.py `.rpaint.json` envelope; add editable **title** field (top bar) feeding `title`. Add **grid** toggle and a **live stats** strip (reads `strokes.count`, current tool/mode) to reach visual parity with the web tool.

### Step 2 — Trace-over-background-image (native) — see §5

### Step 3 (optional, gated on decision #5) — execution-manual `.md` export; etch pen model.

> These are sequenced so the *distribution pipeline* (§6) can ship after Step 0–1; later features are additive releases.

---

## 5. Trace-over-background-image feature (native)

Mirrors the web feature (full spec: `2026-06-22-roost-trace-image-design.md`); native specifics:

- **Model (AppState):** `@Published var traceImage: NSImage?`, `traceOpacity: Double = 0.4`, `traceVisible: Bool = true`. Transient — **not** a stroke, **not** in undo/redo, **not** serialized.
- **Load:** `NSOpenPanel` (content types `.png/.jpeg/.heic/.image`); plus drag-and-drop onto the canvas and paste-from-clipboard (`NSPasteboard`) as niceties.
- **Render:** in `DrawingCanvasView`'s `Canvas` closure, draw the image **immediately after the white fill and before strokes**, inside the already-translated/scaled `ctx` so it tracks pan/zoom automatically. Contain-fit into the `0…CANVAS_F` square preserving aspect ratio (letterbox, centered), at `traceOpacity`. Use `ctx.draw(Image(nsImage:), in: fittedRect)` with `ctx.opacity`.
- **Controls (ToolbarView, new "Trace" section):** Load image, opacity slider (0–100%), show/hide toggle, clear.
- **Persistence:** excluded from `.rpaint.json`, execution manual, and `renderToPNG` (export stays strokes-only). Downscale very large images for canvas perf.

This is low-risk: the `Canvas` pipeline already has the exact insertion point (after `ctx.fill(white)`, before the stroke loop in `DrawingCanvasView.body`).

---

## 6. Signing & distribution (the core)

### 6.0 Wrap the SwiftPM binary into a `.app` bundle
SwiftPM produces a bare executable, not a bundle. A `build-app.sh` assembles:
```
RoostDraw.app/Contents/
  Info.plist            # CFBundleExecutable=RoostDraw, CFBundleIdentifier=art.roostsocial.RoostDraw,
                        # CFBundlePackageType=APPL, LSMinimumSystemVersion=15.0, NSHighResolutionCapable=YES,
                        # NSPrincipalClass=NSApplication, CFBundleShortVersionString=1.0, CFBundleIconFile=RoostDraw.icns
  MacOS/RoostDraw       # from: swift build -c release  (optionally --arch arm64 --arch x86_64 for universal)
  Resources/RoostDraw.icns
  _CodeSignature/       # created by codesign
```
The Info.plist also fixes GUI activation/menus when launched outside Xcode.

### 6.1 Path A — Ad-hoc / self-signed (free, zero-membership)
```bash
swift build -c release
./build-app.sh                       # assemble RoostDraw.app
codesign --force --deep -s - RoostDraw.app   # "-" = ad-hoc
```
- Locally built apps have **no quarantine xattr → run immediately**. Same for binaries fetched by `curl`/node (npm path).
- A `.dmg`/`.zip` downloaded via a **browser** gets quarantined → one-time Gatekeeper prompt. Mitigations to document: **right-click → Open → Open**, or `xattr -dr com.apple.quarantine RoostDraw.app`.
- Cannot be notarized; not ideal for wide public distribution, perfect for personal/dev use.

### 6.2 Path B — Developer ID + notarization (recommended for sharing)
```bash
swift build -c release && ./build-app.sh
codesign --force --options runtime --timestamp \
  --sign "Developer ID Application: <NAME> (<TEAMID>)" RoostDraw.app
ditto -c -k --keepParent RoostDraw.app RoostDraw.zip
# one-time: xcrun notarytool store-credentials roostdraw-notary \
#           --apple-id <id> --team-id <TEAMID> --password <app-specific-pw>
xcrun notarytool submit RoostDraw.zip --keychain-profile roostdraw-notary --wait
xcrun stapler staple RoostDraw.app
hdiutil create -volname RoostDraw -srcfolder RoostDraw.app -ov -format UDZO RoostDraw.dmg
xcrun stapler staple RoostDraw.dmg     # ticket travels with the artifact (offline Gatekeeper OK)
```
- Hardened runtime (`--options runtime`), no entitlements needed (non-sandboxed, local file access). Notarization + stapling → **no Gatekeeper friction anywhere**, including offline.

**`build-app.sh` should default to ad-hoc and switch to Developer ID when `DEVELOPER_ID`/`TEAM_ID` env vars are set**, then notarize+staple. One script, both paths.

### 6.3 Channel 1 — GitHub Releases (canonical)
Upload the **notarized, stapled** `RoostDraw-<version>.dmg` (and `.zip`) to `github.com/ashrocket/roost-draw/releases/v<version>`. This artifact is the single source the other two channels point at.

### 6.4 Channel 2 — Homebrew cask
Tap repo `github.com/ashrocket/homebrew-roostdraw`, file `Casks/roostdraw.rb`:
```ruby
cask "roostdraw" do
  version "1.0.0"
  sha256 "<sha256 of the dmg>"
  url "https://github.com/ashrocket/roost-draw/releases/download/v#{version}/RoostDraw-#{version}.dmg"
  name "RoostDraw"
  desc "MacPaint-style editor for the Roost scratchpad"
  homepage "https://github.com/ashrocket/roost-draw"
  depends_on macos: ">= :sequoia"     # macOS 15
  app "RoostDraw.app"
  zap trash: ["~/Library/Preferences/art.roostsocial.RoostDraw.plist"]
end
```
- User flow: `brew tap ashrocket/roostdraw && brew install --cask roostdraw`.
- **Why notarization matters here:** brew downloads the dmg (quarantined). Because the notarization ticket is **stapled**, Gatekeeper validates **offline** and the app opens with no warning. Ad-hoc-only casks would force `--no-quarantine` (discouraged) or a manual right-click-Open.
- **Alternative — from-source formula:** a Homebrew *formula* that `depends_on xcode` and runs `swift build -c release`, installing the assembled `.app`. Locally compiled → unquarantined → runs even without notarization, at the cost of a build on install.

### 6.5 Channel 3 — npm (convenience fetcher)
Package `roostdraw`, `package.json`:
```jsonc
{
  "name": "roostdraw",
  "version": "1.0.0",
  "bin": { "roostdraw": "bin/roostdraw.js" },
  "os": ["darwin"],
  "cpu": ["arm64", "x64"],
  "scripts": { "postinstall": "node scripts/fetch.js" }
}
```
- `postinstall` fetches the **same GitHub release `.zip`** (a zipped, signed+stapled `RoostDraw.app`), unzips into the package; `bin/roostdraw.js` does `open -a RoostDraw.app` (or execs the inner binary).
- **Caveats to document:** macOS-only (the `os` field aborts installs elsewhere — no cross-platform); ship the **zipped `.app`** (not a bare binary) so the bundle/Info.plist/signature stay intact; node/`curl` downloads are **not quarantined**, so even ad-hoc builds launch cleanly via npm; pin the release `sha256` and verify after download.
- npm is a *convenience* for JS-ecosystem users, **not** the canonical channel.

### 6.6 Recommendation
**Canonical artifact = notarized Developer ID `RoostDraw.app` (`.dmg` + `.zip`) on GitHub Releases**, fronted by the **Homebrew cask** for `brew install --cask roostdraw`, with the **npm** package as a convenience fetcher. **Ad-hoc signing is the zero-cost fallback** when there's no paid membership — fully fine for local use and npm-fetched installs; only browser-downloaded dmgs need a one-time right-click-Open.

---

## 7. Risks / notes
- Universal binary requires both arch slices available in the toolchain; default arm64-only is simplest, add `--arch x86_64` if Intel users matter.
- Renaming touches the nested `controller/.git` repo (it's its own repo) — do the `git mv` there, not in the parent.
- If migrating to `.xcodeproj` later, signing/notarization move into `xcodebuild -exportArchive` with an ExportOptions.plist; the shell-script path above avoids that dependency.
- App icon (`RoostDraw.icns`) is currently absent — needed for a polished release (decision #6 / asset task).
