#!/usr/bin/env python3
"""cutout.py — take the paper out of a photo of a drawing.

    python3 tools/cutout.py tartaruga.png -o tartaruga_cut.png

A drawing photographed or scanned on paper comes with the paper: an off-white
that is never one colour, darker in the corners, with the grain of the sheet in
it. This finds the drawing and writes it on transparency, cropped, ready to be
a sprite (`leo.image("tartaruga_cut.png", 0.4)`) or to be traced
(`tools/trace.py`).

How it decides what is drawing: the paper is pale and grey, and everything the
pencil or the paint touched is either **coloured** or **darker** than the sheet
around it. Both tests are needed — the ink lines are grey, and the painted
areas are pale.

    --tol      how far from the paper's own colour still counts as paper
    --dark     how much darker than the paper counts as a line
    --keep N   keep the N largest pieces (a drawing in separate parts)
    --preview  also write a PNG on a chequerboard, to see the edge
"""

import argparse
import os
import sys

try:
    import numpy as np
    from PIL import Image
    from scipy import ndimage
except ImportError as exc:
    sys.exit(f"this tool needs Pillow, numpy and scipy: pip install Pillow numpy scipy\n({exc})")


def paper_colour(rgb, band=0.04):
    """The sheet, sampled from the border — where a drawing almost never is."""
    h, w, _ = rgb.shape
    b = max(4, int(min(h, w) * band))
    edge = np.concatenate([
        rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3),
        rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3),
    ])
    return np.median(edge, axis=0)


def mask_of(rgb, tol, dark):
    paper = paper_colour(rgb)
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    paper_lum = float(paper @ np.array([0.299, 0.587, 0.114]))

    # Coloured: how far this pixel's hue-ish spread is from the paper's. Using
    # the distance to the paper colour after removing brightness keeps the
    # vignette in the corners from reading as drawing.
    diff = rgb - paper
    tint = diff - diff.mean(axis=2, keepdims=True)
    coloured = np.linalg.norm(tint, axis=2) > tol

    darker = lum < paper_lum - dark
    return coloured | darker


def clean(mask, keep, close=5, min_frac=0.002):
    mask = ndimage.binary_closing(mask, np.ones((close, close)))
    mask = ndimage.binary_opening(mask, np.ones((3, 3)))

    lbl, n = ndimage.label(mask)
    if n == 0:
        return mask
    sizes = ndimage.sum(mask, lbl, range(1, n + 1))
    order = np.argsort(sizes)[::-1]
    floor = mask.size * min_frac
    out = np.zeros_like(mask)
    for i in order[:keep]:
        if sizes[i] >= floor or not out.any():
            out |= (lbl == i + 1)

    # A drawing is a closed outline with paint inside it; the holes belong to
    # the drawing, the paper outside it does not.
    return ndimage.binary_fill_holes(out)


def main():
    ap = argparse.ArgumentParser(description="Take the paper out of a photo of a drawing.")
    ap.add_argument("input")
    ap.add_argument("-o", "--out", help="default: <input>_cut.png")
    ap.add_argument("--tol", type=float, default=14.0, help="colour distance from the paper")
    ap.add_argument("--dark", type=float, default=26.0, help="how much darker than the paper is a line")
    ap.add_argument("--keep", type=int, default=1, help="how many pieces to keep")
    ap.add_argument("--margin", type=int, default=8, help="pixels left around the crop")
    ap.add_argument("--feather", type=float, default=1.0, help="soften the edge, in pixels")
    ap.add_argument("--shrink", type=int, default=0,
                    help="pull the edge in this many pixels. A photographed drawing "
                         "keeps a rim of paper around it, which reads as a pale halo "
                         "once the sprite is over a dark stage")
    ap.add_argument("--no-crop", action="store_true")
    ap.add_argument("--width", type=int, default=0,
                    help="write it this many pixels wide. A sprite has to: every "
                         "picture in an artwork is composed into one 1024x1024 "
                         "sheet, so a 1800 px photo does not fit")
    ap.add_argument("--preview", action="store_true", help="also write a chequerboard version")
    args = ap.parse_args()

    im = Image.open(args.input).convert("RGB")
    rgb = np.asarray(im, dtype=np.float64)

    mask = clean(mask_of(rgb, args.tol, args.dark), args.keep)
    if not mask.any():
        sys.exit("no drawing found — try a smaller --tol or --dark")

    if args.shrink > 0:
        mask = ndimage.binary_erosion(mask, np.ones((3, 3)), iterations=args.shrink)

    alpha = mask.astype(np.float64)
    if args.feather > 0:
        alpha = ndimage.gaussian_filter(alpha, args.feather)
        alpha = np.clip((alpha - 0.35) / 0.4, 0, 1)

    out = np.dstack([np.asarray(im, dtype=np.uint8),
                     (alpha * 255).astype(np.uint8)])
    pic = Image.fromarray(out, "RGBA")

    if not args.no_crop:
        ys, xs = np.where(mask)
        m = args.margin
        box = (max(0, xs.min() - m), max(0, ys.min() - m),
               min(im.width, xs.max() + 1 + m), min(im.height, ys.max() + 1 + m))
        pic = pic.crop(box)

    if args.width > 0 and pic.width != args.width:
        pic = pic.resize((args.width, max(1, round(pic.height * args.width / pic.width))),
                         Image.LANCZOS)

    dest = args.out or os.path.splitext(args.input)[0] + "_cut.png"
    pic.save(dest)

    covered = 100.0 * mask.sum() / mask.size
    print(f"[cutout] {im.width}x{im.height} -> {pic.width}x{pic.height}, "
          f"{covered:.1f}% of the photo was drawing -> {dest}", file=sys.stderr)

    if args.preview:
        board = Image.new("RGB", pic.size)
        px = board.load()
        for y in range(board.height):
            for x in range(board.width):
                px[x, y] = (60, 60, 68) if (x // 16 + y // 16) % 2 else (40, 40, 46)
        board.paste(pic, (0, 0), pic)
        prev = os.path.splitext(dest)[0] + "_preview.png"
        board.save(prev)
        print(f"[cutout] preview -> {prev}", file=sys.stderr)


if __name__ == "__main__":
    main()
