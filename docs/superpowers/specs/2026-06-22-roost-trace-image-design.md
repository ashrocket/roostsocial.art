# Roost Trace-Over-Image — Design

**Date:** 2026-06-22
**Component:** `roost_sim/viewer.html` (primary) + brief `controller/PigeonPaint` (Swift) note
**Status:** Draft for user review. Companion spec: `2026-06-22-roost-swift-app-design.md`.

## Goal

Let the user load a reference image (e.g. a papercut silhouette of two people on a
tandem bicycle), display it dimmed *beneath* the drawing, and trace it with the
existing MacPaint/etch tools to produce normal Roost strokes. The reference is a
**guide only** — it must never become stroke data or pollute the `.rpaint.json` /
execution manual that drive the real scratchpad.

## Open decisions for the user

1. **Persistence:** default **session-only** (guide vanishes on reload), with an
   opt-in "Embed trace in saved file" checkbox that writes a *sibling* `trace`
   field (never inside `strokes`). Recommended: session-only default. ← needs confirm
2. **Filters:** ship **opacity + grayscale + invert**; defer threshold/posterize. ← confirm scope
3. **"New" clears the trace; "Clear"/"Shake" keeps it** (so you can re-trace the
   same reference). ← confirm
4. **Shortcut `b`** toggles trace visibility (`b` = background); `[` / `]` dim /
   brighten. All currently unused. ← confirm
5. **Formats:** PNG/JPEG/WebP/SVG via `<img>` + data URL. ← confirm SVG wanted

## Assumptions

- Reference images are local user files (loaded as data URLs) → canvas stays
  un-tainted; `toBlob` PNG export keeps working.
- Non-square references are **contain-fit** (letterboxed), centered in the square
  canvas. The bicycle sample is portrait (~457×556) → margins left/right.
- One reference image at a time (replacing loads a new one).

## Data model (the load-bearing decision)

The reference lives in a **new transient `state.trace` object, entirely separate
from `state.strokes`.** Because `rpaintData()` (viewer.html:943) and
`validateStrokes()` (:916) serialize *only* `state.strokes`, and `manualData()`
(:989) + Python `sim.py load_rpaint`/`replay.py`/`roostpaint.py` consume *only*
`drawing.strokes`, the trace is automatically excluded from every artifact that
reaches the real Roost device. This is the safest possible boundary: the guide
*cannot* leak into a stroke because the two never share a container.

```js
// added to state (viewer.html:463-484)
trace: {
  image: null,      // HTMLImageElement; transient, never serialized into strokes
  visible: true,
  opacity: 0.35,
  grayscale: false,
  invert: false,
  name: null,       // source filename, for the status line
}
```

**Optional opt-in persistence** (decision 1): if "Embed trace" is on, `rpaintData()`
adds a top-level sibling `trace: { dataUrl, opacity }`. Loaders ignore unknown
top-level keys (`loadPayload` reads `data.strokes || data.drawing.strokes`;
`sim.py` reads only `strokes`), so round-tripping stays clean — sim.py simply drops
the field on re-save. Never place image data inside a `strokes` entry: sim.py
`normalize_strokes` would raise `ValueError`.

**PNG export is already clean:** `exportPng()` (:1125) renders strokes onto a fresh
offscreen canvas and never touches `state.trace`, so the exported art excludes the
reference with zero extra work. (A future "export with reference" overlay is YAGNI.)

## UX / layout

New **`Trace`** toolbar section, inserted *before* the existing `Files` section
(viewer.html:396). Controls:

- **Load image** button → opens a dedicated hidden `#traceInput`
  (`accept="image/*"`), kept separate from `#fileInput` so image vs `.rpaint`
  loading never collide.
- **Show/Hide** toggle (button text flips, `.active` when shown).
- **Clear** (removes the reference; strokes untouched).
- **Opacity** slider (0–100, default 35) reusing the existing `.slider-row` grid.
- **Grayscale** and **Invert** toggle buttons (help a flat silhouette read).
- Plus **drag-and-drop onto the canvas** and **clipboard paste** as load paths.

## Render ordering

`drawAll()` (viewer.html:613-622) gains one call, between the white fill and the
strokes loop:

```
white fillRect (:615-616)
→ drawTraceImage()      // NEW: dimmed reference
→ strokes (:617)
→ draft preview (:618)
→ drawEtchCursor (:619)
```

The image is drawn in `VIEW_SIZE` coordinates (same space as `pxPoint`), so the
existing `setTransform(dpr,…)` (:592) handles Retina, and CSS-only zoom
(`setZoom`, :1249, resizes the shell) needs no change. The CSS grid background is
independent (it's on the shell element).

```js
function drawTraceImage() {
  const t = state.trace;
  if (!t.image || !t.visible || t.opacity <= 0) return;
  const { width: iw, height: ih } = t.image;
  const scale = Math.min(VIEW_SIZE / iw, VIEW_SIZE / ih);   // contain
  const w = iw * scale, h = ih * scale;
  const x = (VIEW_SIZE - w) / 2, y = (VIEW_SIZE - h) / 2;    // centered
  ctx.save();
  ctx.globalAlpha = t.opacity;
  const f = `${t.grayscale ? "grayscale(1) " : ""}${t.invert ? "invert(1)" : ""}`.trim();
  if (f) ctx.filter = f;
  ctx.drawImage(t.image, x, y, w, h);
  ctx.restore();
}

function loadTraceImage(file) {
  if (!file || !file.type.startsWith("image/")) return;
  const reader = new FileReader();
  reader.onload = () => {
    const img = new Image();
    img.onload = () => {
      state.trace.image = img; state.trace.visible = true; state.trace.name = file.name;
      drawAll(); setStatus(`Trace: ${file.name}`);
    };
    img.onerror = () => window.alert("Could not load that image.");
    img.src = String(reader.result);           // data URL → no canvas taint
  };
  reader.readAsDataURL(file);
}
```

## Implementation map (viewer.html)

| Location | Change |
|---|---|
| CSS, before `.hidden` (:287) | `.trace-row` layout; reuse `.slider-row`, `.file-grid` |
| Toolbar HTML, before `Files` section (:396) | new `<section>` with `#traceInput`(hidden), `#traceLoadBtn`, `#traceToggleBtn`, `#traceClearBtn`, `#traceOpacity`, `#traceGray`, `#traceInvert` |
| `state` (:463-484) | add `trace` object (above) |
| `el` map (:486-525) | add the seven `#trace*` element handles |
| `drawAll()` (:613-622) | insert `drawTraceImage()` after white fill, before strokes |
| new fns near `drawEtchCursor` (:596) | `drawTraceImage()`, `loadTraceImage(file)` |
| listeners block (:1278-1299) | wire load/toggle/clear/opacity/gray/invert |
| canvas listeners (:1306-1310) | `dragover`+`drop` on `el.shell` (image→trace, else `openFile`); `window` `paste` → image item |
| keydown (:1312-1354) | `b` toggle visibility; `[`/`]` opacity −/+ |
| `updateUi()` (:1220-1247) | reflect toggle `.active`, opacity label, disable toggle/clear when no image |
| `newDrawing()` (:842) | also null the trace; `clearDrawing()`/`Shake` leave it |

No existing function signature changes; all additions are purely additive.

## Native PigeonPaint equivalent (brief)

Mirror in `controller/PigeonPaint` per `2026-06-22-roost-swift-app-design.md`:
add `traceImage: NSImage?`, `traceOpacity`, `traceVisible`, `traceGrayscale`,
`traceInvert` to `AppState`; in `DrawingCanvasView.draw`, render the `CGImage`
contain-fit behind the stroke layer at `traceOpacity` (CIFilter for grayscale/
invert). Load via `NSOpenPanel` (image UTTypes), `NSDraggingDestination`, and
`NSPasteboard`. Exclude `traceImage` from the rpaint `Encodable` exactly as the web
keeps it out of `strokes`.

## Testing

- Load PNG/JPEG/SVG → appears centered, dimmed; opacity slider + grayscale/invert
  visibly change it; Hide/Clear behave; drag-drop and paste load it.
- Draw strokes over it → Save `.rpaint.json` and Manual → confirm **no `trace`/
  image bytes inside `strokes`** and that `python -c "import sim; sim.load_rpaint(...)"`
  round-trips cleanly.
- Export PNG → reference absent from output.
- Non-square + portrait references letterbox correctly; `b`/`[`/`]` shortcuts work
  and don't fire while typing in inputs.
