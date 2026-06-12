#!/usr/bin/env python3
"""Simulator for the Roost scratchpad canvas.

Models what I can actually do through computer-use mouse events:
  - strokes are polylines drawn with mouse_down / mouse_move / mouse_up
  - fast moves  -> THICK ink (~7px on the ~265px-wide real canvas)
  - slow moves  -> THIN ink  (~3px)
  - palette: the 6 swatches in the app (black, white, red, blue, green, yellow)
  - white background, opaque ink, later strokes cover earlier ones

Coordinates in stroke definitions are normalized [0..1] x [0..1] so the same
artwork renders at any canvas size (40, 100, 265, ...).
"""
from PIL import Image, ImageDraw

PALETTE = {
    "black":  (17, 17, 17),
    "white":  (255, 255, 255),
    "red":    (210, 65, 60),
    "blue":   (69, 131, 214),
    "green":  (93, 158, 88),
    "yellow": (231, 182, 60),
}

# stroke width as a fraction of canvas size (measured on the real canvas:
# thick ~7px / 265px, thin ~3px / 265px)
THICK_FRAC = 7.0 / 265.0
THIN_FRAC = 3.0 / 265.0
SS = 4  # supersample factor


def render(strokes, size, bg="white"):
    """strokes: list of (color, mode, [(u,v), ...]) with u,v in 0..1."""
    W = size * SS
    img = Image.new("RGB", (W, W), PALETTE[bg])
    d = ImageDraw.Draw(img)
    for color, mode, pts in strokes:
        col = PALETTE[color]
        frac = THICK_FRAC if mode == "thick" else THIN_FRAC
        w = max(1, round(frac * size * SS))
        px = [(u * (W - 1), v * (W - 1)) for u, v in pts]
        if len(px) == 1:
            x, y = px[0]
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=col)
            continue
        for (x0, y0), (x1, y1) in zip(px, px[1:]):
            d.line([x0, y0, x1, y1], fill=col, width=w)
        for x, y in px:  # round caps/joints
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=col)
    return img.resize((size, size), Image.LANCZOS)


def save(strokes, size, path, scale_to=320):
    img = render(strokes, size)
    img.save(path)
    # also save an upscaled preview (nearest) so tiny canvases are inspectable
    big = img.resize((scale_to, scale_to), Image.NEAREST)
    big.save(path.replace(".png", "_big.png"))
    return img


def contact_sheet(images, labels, cols, cell=160, path="sheet.png"):
    rows = (len(images) + cols - 1) // cols
    pad = 24
    sheet = Image.new("RGB", (cols * (cell + pad) + pad, rows * (cell + pad + 14) + pad), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(zip(images, labels)):
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = pad + r * (cell + pad + 14)
        sheet.paste(im.resize((cell, cell), Image.NEAREST), (x, y))
        d.text((x, y + cell + 2), lab, fill=(230, 230, 230))
    sheet.save(path)
