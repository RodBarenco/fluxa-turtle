#!/usr/bin/env python3
"""trace.py — turn a drawing into Fluxa Turtle code.

    python3 tools/trace.py logo.svg -o art.flx
    python3 tools/trace.py sketch.png --turtles 4 -o art.flx

It reads an SVG (no dependencies) or a raster image (needs Pillow), turns every
outline it finds into a run of `toward` steps, and writes Fluxa you can paste
into `main.flx`. What comes out is ordinary turtle code: it animates, it obeys
`pivot`, `shift` and `erase`, and you can edit any line of it.

SVG is the input that keeps its shape — it is already made of curves, so it is
sampled, not guessed at. A raster image is traced by outlining the dark areas,
which works on line art, logos and silhouettes, and does not work on
photographs.

The two numbers to keep an eye on are printed at the end: how many steps the
drawing costs (the stage holds 6000) and how many turtles it uses (32). If it
does not fit, --max-steps simplifies until it does.
"""

import argparse
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

# ── geometry ──────────────────────────────────────────────────────────────

class Sub:
    """One continuous outline: the points, its colour, and whether it closes."""

    def __init__(self, pts, color=None, closed=False):
        self.pts = pts
        self.color = color
        self.closed = closed

    def length(self):
        return sum(math.dist(a, b) for a, b in zip(self.pts, self.pts[1:]))


def rdp(pts, eps):
    """Ramer-Douglas-Peucker: drop the points that do not change the shape."""
    if eps <= 0 or len(pts) < 3:
        return pts
    ax, ay = pts[0]
    bx, by = pts[-1]
    dx, dy = bx - ax, by - ay
    span = math.hypot(dx, dy)
    worst, at = -1.0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        if span == 0:
            d = math.hypot(px - ax, py - ay)
        else:
            d = abs(dy * px - dx * py + bx * ay - by * ax) / span
        if d > worst:
            worst, at = d, i
    if worst <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:at + 1], eps)[:-1] + rdp(pts[at:], eps)


def dedupe(pts, eps=0.01):
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > eps:
            out.append(p)
    return out


# ── SVG: transforms ───────────────────────────────────────────────────────

def mat_mul(m, n):
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B,
            a * C + c * D, b * C + d * D,
            a * E + c * F + e, b * E + d * F + f)


def mat_apply(m, p):
    a, b, c, d, e, f = m
    x, y = p
    return (a * x + c * y + e, b * x + d * y + f)


IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
NUM = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def parse_transform(text):
    """translate, scale, rotate, matrix, skewX, skewY — chained left to right."""
    m = IDENTITY
    if not text:
        return m
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", text):
        v = [float(x) for x in NUM.findall(args)]
        if name == "translate":
            m = mat_mul(m, (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0))
        elif name == "scale":
            sx = v[0]
            sy = v[1] if len(v) > 1 else sx
            m = mat_mul(m, (sx, 0, 0, sy, 0, 0))
        elif name == "rotate":
            a = math.radians(v[0])
            r = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0)
            if len(v) >= 3:
                m = mat_mul(m, (1, 0, 0, 1, v[1], v[2]))
                m = mat_mul(m, r)
                m = mat_mul(m, (1, 0, 0, 1, -v[1], -v[2]))
            else:
                m = mat_mul(m, r)
        elif name == "matrix" and len(v) >= 6:
            m = mat_mul(m, tuple(v[:6]))
        elif name == "skewX":
            m = mat_mul(m, (1, 0, math.tan(math.radians(v[0])), 1, 0, 0))
        elif name == "skewY":
            m = mat_mul(m, (1, math.tan(math.radians(v[0])), 0, 1, 0, 0))
    return m


# ── SVG: colours ──────────────────────────────────────────────────────────

NAMED = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0),
    "orange": (255, 165, 0), "purple": (128, 0, 128), "gray": (128, 128, 128),
    "grey": (128, 128, 128), "cyan": (0, 255, 255), "magenta": (255, 0, 255),
    "pink": (255, 192, 203), "brown": (165, 42, 42), "navy": (0, 0, 128),
}


def parse_color(text):
    if not text:
        return None
    t = text.strip().lower()
    if t in ("none", "transparent", "currentcolor"):
        return None
    if t in NAMED:
        return NAMED[t]
    if t.startswith("#"):
        h = t[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) >= 6:
            try:
                return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                return None
    m = re.match(r"rgba?\(([^)]*)\)", t)
    if m:
        v = [float(x) for x in NUM.findall(m.group(1))][:3]
        if len(v) == 3:
            return tuple(min(255, max(0, int(round(x)))) for x in v)
    return None


def element_color(el, inherited):
    style = {}
    for part in (el.get("style") or "").split(";"):
        if ":" in part:
            k, _, v = part.partition(":")
            style[k.strip()] = v.strip()
    for key in ("stroke", "fill"):
        c = parse_color(style.get(key) or el.get(key))
        if c:
            return c
    return inherited


# ── SVG: the `d` attribute ────────────────────────────────────────────────

TOKENS = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])|([-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?)")


def bezier3(p0, p1, p2, p3, n):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                    u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]))
    return out


def bezier2(p0, p1, p2, n):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def curve_steps(pts, density):
    """Samples per curve, from the length of its control polygon."""
    poly = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    return max(4, min(160, int(poly / max(0.5, density))))


def arc_points(p0, rx, ry, phi, large, sweep, p1, density):
    """Endpoint arc -> centre parametrisation (SVG spec F.6.5), then sampled."""
    if rx == 0 or ry == 0 or p0 == p1:
        return [p1]
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(phi % 360)
    cs, sn = math.cos(phi), math.sin(phi)
    dx2, dy2 = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1, y1 = cs * dx2 + sn * dy2, -sn * dx2 + cs * dy2
    lam = (x1 * x1) / (rx * rx) + (y1 * y1) / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        co = -co
    cxp, cyp = co * rx * y1 / ry, -co * ry * x1 / rx
    cx = cs * cxp - sn * cyp + (p0[0] + p1[0]) / 2
    cy = sn * cxp + cs * cyp + (p0[1] + p1[1]) / 2

    def ang(ux, uy, vx, vy):
        d = (ux * vx + uy * vy) / (math.hypot(ux, uy) * math.hypot(vx, vy))
        a = math.acos(max(-1.0, min(1.0, d)))
        return -a if ux * vy - uy * vx < 0 else a

    t0 = ang(1, 0, (x1 - cxp) / rx, (y1 - cyp) / ry)
    dt = ang((x1 - cxp) / rx, (y1 - cyp) / ry, (-x1 - cxp) / rx, (-y1 - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    if sweep and dt < 0:
        dt += 2 * math.pi
    n = max(4, min(180, int(abs(dt) * max(rx, ry) / max(0.5, density))))
    out = []
    for i in range(1, n + 1):
        t = t0 + dt * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cs * x - sn * y + cx, sn * x + cs * y + cy))
    return out


def parse_path(d, density):
    """Returns a list of point lists — one per subpath — plus their closed flag."""
    toks = []
    for cmd, num in TOKENS.findall(d or ""):
        toks.append(cmd if cmd else float(num))

    subs, pts = [], []
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    cmd = None
    prev_c2 = None      # for S/s
    prev_q1 = None      # for T/t
    i = 0

    def flush(closed):
        if len(pts) > 1:
            subs.append((list(pts), closed))

    while i < len(toks):
        t = toks[i]
        if isinstance(t, str):
            cmd = t
            i += 1
            if cmd in "Zz":
                if pts:
                    pts.append(start)
                    flush(True)
                pts = []
                cur = start
                prev_c2 = prev_q1 = None
                continue
        if cmd is None:
            i += 1
            continue

        rel = cmd.islower()
        c = cmd.upper()

        def take(n):
            nonlocal i
            v = toks[i:i + n]
            i += n
            if len(v) < n or any(isinstance(x, str) for x in v):
                return None
            return [float(x) for x in v]

        if c == "M":
            v = take(2)
            if v is None:
                break
            p = (cur[0] + v[0], cur[1] + v[1]) if rel else (v[0], v[1])
            flush(False)
            pts = [p]
            cur = start = p
            cmd = "l" if rel else "L"      # further pairs are implicit linetos
            prev_c2 = prev_q1 = None
        elif c == "L":
            v = take(2)
            if v is None:
                break
            p = (cur[0] + v[0], cur[1] + v[1]) if rel else (v[0], v[1])
            pts.append(p)
            cur = p
            prev_c2 = prev_q1 = None
        elif c == "H":
            v = take(1)
            if v is None:
                break
            p = (cur[0] + v[0], cur[1]) if rel else (v[0], cur[1])
            pts.append(p)
            cur = p
            prev_c2 = prev_q1 = None
        elif c == "V":
            v = take(1)
            if v is None:
                break
            p = (cur[0], cur[1] + v[0]) if rel else (cur[0], v[0])
            pts.append(p)
            cur = p
            prev_c2 = prev_q1 = None
        elif c in ("C", "S"):
            v = take(4 if c == "S" else 6)
            if v is None:
                break
            if c == "C":
                c1 = (cur[0] + v[0], cur[1] + v[1]) if rel else (v[0], v[1])
                c2 = (cur[0] + v[2], cur[1] + v[3]) if rel else (v[2], v[3])
                end = (cur[0] + v[4], cur[1] + v[5]) if rel else (v[4], v[5])
            else:
                c1 = (2 * cur[0] - prev_c2[0], 2 * cur[1] - prev_c2[1]) if prev_c2 else cur
                c2 = (cur[0] + v[0], cur[1] + v[1]) if rel else (v[0], v[1])
                end = (cur[0] + v[2], cur[1] + v[3]) if rel else (v[2], v[3])
            pts.extend(bezier3(cur, c1, c2, end, curve_steps([cur, c1, c2, end], density)))
            cur, prev_c2, prev_q1 = end, c2, None
        elif c in ("Q", "T"):
            v = take(2 if c == "T" else 4)
            if v is None:
                break
            if c == "Q":
                q1 = (cur[0] + v[0], cur[1] + v[1]) if rel else (v[0], v[1])
                end = (cur[0] + v[2], cur[1] + v[3]) if rel else (v[2], v[3])
            else:
                q1 = (2 * cur[0] - prev_q1[0], 2 * cur[1] - prev_q1[1]) if prev_q1 else cur
                end = (cur[0] + v[0], cur[1] + v[1]) if rel else (v[0], v[1])
            pts.extend(bezier2(cur, q1, end, curve_steps([cur, q1, end], density)))
            cur, prev_q1, prev_c2 = end, q1, None
        elif c == "A":
            v = take(7)
            if v is None:
                break
            end = (cur[0] + v[5], cur[1] + v[6]) if rel else (v[5], v[6])
            pts.extend(arc_points(cur, v[0], v[1], v[2], v[3] >= 0.5, v[4] >= 0.5, end, density))
            cur = end
            prev_c2 = prev_q1 = None
        else:
            i += 1

    flush(False)
    return subs


# ── SVG: the document ─────────────────────────────────────────────────────

def strip_ns(tag):
    return tag.split("}", 1)[-1]


def read_svg(path, density):
    root = ET.parse(path).getroot()
    subs = []

    def walk(el, mat, color):
        mat = mat_mul(mat, parse_transform(el.get("transform")))
        color = element_color(el, color)
        tag = strip_ns(el.tag)

        raw = []
        if tag == "path":
            raw = parse_path(el.get("d"), density)
        elif tag == "line":
            f = lambda k: float(el.get(k, 0))
            raw = [([(f("x1"), f("y1")), (f("x2"), f("y2"))], False)]
        elif tag in ("polyline", "polygon"):
            v = [float(x) for x in NUM.findall(el.get("points", ""))]
            pl = list(zip(v[0::2], v[1::2]))
            if tag == "polygon" and pl:
                pl.append(pl[0])
            raw = [(pl, tag == "polygon")]
        elif tag == "rect":
            f = lambda k: float(el.get(k, 0))
            x, y, w, h = f("x"), f("y"), f("width"), f("height")
            raw = [([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], True)]
        elif tag in ("circle", "ellipse"):
            f = lambda k, d=0: float(el.get(k, d))
            cx, cy = f("cx"), f("cy")
            if tag == "circle":
                rx = ry = f("r")
            else:
                rx, ry = f("rx"), f("ry")
            n = max(16, min(180, int(max(rx, ry) * 2 / max(0.5, density))))
            pl = [(cx + rx * math.cos(2 * math.pi * i / n),
                   cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
            raw = [(pl, True)]

        for pl, closed in raw:
            if len(pl) > 1:
                subs.append(Sub([mat_apply(mat, p) for p in pl], color, closed))

        for kid in el:
            walk(kid, mat, color)

    walk(root, IDENTITY, None)

    # viewBox: the coordinates the file is actually written in
    box = root.get("viewBox")
    if box:
        v = [float(x) for x in NUM.findall(box)]
        if len(v) == 4 and v[2] > 0 and v[3] > 0:
            for s in subs:
                s.pts = [(p[0] - v[0], p[1] - v[1]) for p in s.pts]
    return subs


# ── raster: outline the dark areas ────────────────────────────────────────

def read_raster(path, threshold, invert, blur=0.0):
    try:
        from PIL import Image
    except ImportError:
        sys.exit("a raster image needs Pillow:  pip install Pillow\n"
                 "(an SVG needs nothing at all)")

    im = Image.open(path)
    # A cut-out arrives with transparency, and "transparent" has to mean paper
    # here, not ink: composited onto white it traces the drawing and not the
    # hole it was cut from.
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        sheet = Image.new("RGBA", im.size, (255, 255, 255, 255))
        sheet.paste(im, (0, 0), im)
        im = sheet
    im = im.convert("L")
    if blur > 0:
        from PIL import ImageFilter
        im = im.filter(ImageFilter.GaussianBlur(blur))
    w, h = im.size
    scale = 1.0
    if max(w, h) > 900:                 # tracing a huge photo helps nobody
        scale = 900 / max(w, h)
        w, h = int(w * scale), int(h * scale)
        im = im.resize((w, h))
    px = im.load()

    # One border of background all round, so a shape touching the edge of the
    # image still has an outline to walk.
    ink = [[False] * (w + 2) for _ in range(h + 2)]
    for y in range(h):
        for x in range(w):
            dark = px[x, y] < threshold
            ink[y + 1][x + 1] = (not dark) if invert else dark

    # Moore boundary following. A pixel that is ink with background to its left
    # starts a border — which finds the outside of every shape and, scanning on
    # into it, the inside of every hole as well. Each border is walked once and
    # its pixels are marked, so the next scan line does not walk it again.
    seen = set()
    subs = []
    for y in range(1, h + 1):
        for x in range(1, w + 1):
            if not ink[y][x] or ink[y][x - 1] or (x, y) in seen:
                continue
            loop = moore(ink, (x, y), w, h)
            for p in loop:
                seen.add(p)
            if len(loop) > 12:
                subs.append(Sub([((p[0] - 1) / scale, (p[1] - 1) / scale) for p in loop],
                                None, True))
    return subs


NEIGH = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def moore(ink, start, w, h, limit=200000):
    """Walks one border clockwise and comes back to where it set off."""
    cur = start
    prev = (start[0] - 1, start[1])      # the background pixel we came from
    loop = [start]
    for _ in range(limit):
        d = NEIGH.index((prev[0] - cur[0], prev[1] - cur[1]))
        nxt = None
        for k in range(1, 9):
            off = NEIGH[(d + k) % 8]
            p = (cur[0] + off[0], cur[1] + off[1])
            if 0 <= p[0] <= w + 1 and 0 <= p[1] <= h + 1 and ink[p[1]][p[0]]:
                back = NEIGH[(d + k - 1) % 8]
                nxt = p
                prev = (cur[0] + back[0], cur[1] + back[1])
                break
        if nxt is None:                  # a single pixel, nothing to walk
            break
        cur = nxt
        loop.append(cur)
        if cur == start and len(loop) > 2:
            break
    return loop


# ── fitting and emitting ──────────────────────────────────────────────────

def fit(subs, W, H, margin):
    xs = [p[0] for s in subs for p in s.pts]
    ys = [p[1] for s in subs for p in s.pts]
    if not xs:
        return
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sw, sh = max(1e-6, x1 - x0), max(1e-6, y1 - y0)
    k = min((W - 2 * margin) / sw, (H - 2 * margin) / sh)
    ox = (W - sw * k) / 2 - x0 * k
    oy = (H - sh * k) / 2 - y0 * k
    for s in subs:
        s.pts = [(p[0] * k + ox, p[1] * k + oy) for p in s.pts]


def simplify(subs, tol, min_points):
    out = []
    for s in subs:
        pts = dedupe(s.pts)
        if tol > 0:
            pts = rdp(pts, tol)
        if len(pts) >= max(2, min_points):
            out.append(Sub(pts, s.color, s.closed))
    return out


def total_steps(groups):
    """Turtles draw in parallel, so the cost is the longest one's."""
    return max((sum(len(s.pts) for s in g) for g in groups), default=0)


def split(subs, n):
    """Longest outline to the emptiest turtle: keeps the parallel runs even."""
    groups = [[] for _ in range(n)]
    load = [0.0] * n
    for s in sorted(subs, key=lambda s: -s.length()):
        i = load.index(min(load))
        groups[i].append(s)
        load[i] += len(s.pts)
    return [g for g in groups if g]


PALETTE = [(120, 208, 214), (255, 200, 60), (255, 120, 90), (150, 200, 120),
           (200, 150, 255), (240, 240, 245), (90, 230, 180), (255, 160, 200)]


def emit_svg(subs, src, W, H, stroke, color, keep):
    """The same outlines, as an SVG — the drawing vectorised, not turtle code."""
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'  <!-- traced from {os.path.basename(src)} by tools/trace.py -->']
    for i, sb in enumerate(subs):
        c = color or (sb.color if keep and sb.color else PALETTE[i % len(PALETTE)])
        pts = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in sb.pts)
        shut = "Z" if sb.closed else ""
        d = "M " + pts.replace(" ", " L ", 1).replace(",", " ", 1)
        out.append(f'  <polyline points="{pts}" fill="none" '
                   f'stroke="rgb({c[0]},{c[1]},{c[2]})" stroke-width="{stroke}" '
                   f'stroke-linejoin="round" stroke-linecap="round"/>')
    out.append("</svg>")
    return "\n".join(out)


def emit(groups, src, speed, stroke, color, keep, W, H):
    n_actions = sum(len(s.pts) for g in groups for s in g)
    steps = total_steps(groups)
    out = []
    out.append(f"// ── traced from {os.path.basename(src)} by tools/trace.py ──")
    out.append(f"// {len(groups)} turtles . {steps} steps . {n_actions} actions . stage {W}x{H}")
    out.append("//")
    out.append("// Paste this between the stage and the execution line of main.flx.")
    out.append("// It is ordinary turtle code: change a colour, a width or a speed and")
    out.append("// save. Press R to watch it drawn from the beginning.")
    out.append("")
    for gi, g in enumerate(groups):
        name = f"t{gi}"
        first = g[0].pts[0]
        base = color or (g[0].color if keep and g[0].color else PALETTE[gi % len(PALETTE)])
        out.append(f"Block {name} typeof turtle.Turtle")
        out.append(f"{name}.spawn({first[0]:.1f}, {first[1]:.1f})")
        out.append(f"{name}.hide()")
        out.append(f"{name}.speed({speed:.1f})")
        out.append(f"{name}.path_width({stroke})")
        out.append(f"{name}.path_color({base[0]}, {base[1]}, {base[2]})")
        step = 1
        for si, s in enumerate(g):
            if keep and s.color and s.color != base and not color:
                base = s.color
                out.append(f"{name}.path_color({base[0]}, {base[1]}, {base[2]})")
            pts = s.pts
            if si == 0:
                out.append(f"{name}.jump({step}, {pts[0][0]:.1f}, {pts[0][1]:.1f})")
            else:
                out.append(f"// outline {si + 1}")
                out.append(f"{name}.jump({step}, {pts[0][0]:.1f}, {pts[0][1]:.1f})")
            step += 1
            for p in pts[1:]:
                out.append(f"{name}.toward({step}, {p[0]:.1f}, {p[1]:.1f})")
                step += 1
        out.append("")
    return "\n".join(out)


# ── the tool ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Turn an SVG or a raster image into Fluxa Turtle code.")
    ap.add_argument("input", help="an .svg, or a .png/.jpg (needs Pillow)")
    ap.add_argument("-o", "--out", help="write here instead of stdout")
    ap.add_argument("--emit", choices=("flx", "svg"), default="flx",
                    help="turtle code (default), or the outlines as an SVG")
    ap.add_argument("--turtles", type=int, default=1,
                    help="draw with this many turtles, in parallel (max 32)")
    ap.add_argument("--stage", default="800x600", help="stage size, WxH")
    ap.add_argument("--margin", type=float, default=40.0)
    ap.add_argument("--max-steps", type=int, default=1500,
                    help="simplify until the drawing costs at most this many steps")
    ap.add_argument("--tolerance", type=float, default=-1.0,
                    help="simplification, in pixels; -1 finds it from --max-steps")
    ap.add_argument("--density", type=float, default=6.0,
                    help="one sample per this many pixels of curve")
    ap.add_argument("--speed", type=float, default=900.0)
    ap.add_argument("--stroke", type=int, default=2, help="path_width")
    ap.add_argument("--color", help="one colour for everything, as R,G,B")
    ap.add_argument("--keep-colors", action="store_true",
                    help="use the colours in the SVG instead of the palette")
    ap.add_argument("--min-points", type=int, default=3,
                    help="drop outlines shorter than this many points")
    ap.add_argument("--threshold", type=int, default=128,
                    help="raster only: a pixel darker than this is ink")
    ap.add_argument("--blur", type=float, default=0.0,
                    help="raster: smooth this many pixels before deciding what is ink. "
                         "A pencil line photographed on paper is grainy and comes out as "
                         "a cloud of specks without it")
    ap.add_argument("--invert", action="store_true",
                    help="raster only: trace the light areas instead")
    args = ap.parse_args()

    try:
        W, H = (int(v) for v in args.stage.lower().split("x"))
    except ValueError:
        sys.exit("--stage wants something like 800x600")

    if args.turtles < 1 or args.turtles > 32:
        sys.exit("--turtles is between 1 and 32 (the stage holds 32)")

    color = None
    if args.color:
        v = [int(x) for x in NUM.findall(args.color)][:3]
        if len(v) != 3:
            sys.exit("--color wants R,G,B")
        color = tuple(v)

    ext = os.path.splitext(args.input)[1].lower()
    if ext == ".svg":
        subs = read_svg(args.input, args.density)
    else:
        subs = read_raster(args.input, args.threshold, args.invert, args.blur)

    subs = [s for s in subs if len(s.pts) > 1]
    if not subs:
        sys.exit("nothing to draw was found in that file")

    fit(subs, W, H, args.margin)

    # Simplify to fit the step budget. The tolerance is searched, not guessed:
    # doubling it until the drawing fits is enough and takes milliseconds.
    tol = args.tolerance if args.tolerance >= 0 else 0.0
    kept = simplify(subs, tol, args.min_points)
    if args.tolerance < 0:
        while total_steps(split(kept, args.turtles)) > args.max_steps and tol < 64:
            tol = 0.4 if tol == 0 else tol * 1.6
            kept = simplify(subs, tol, args.min_points)
    if not kept:
        sys.exit("everything was simplified away — try --min-points 2 or --tolerance 0")

    groups = split(kept, args.turtles)
    if args.emit == "svg":
        code = emit_svg(kept, args.input, W, H, args.stroke, color, args.keep_colors)
    else:
        code = emit(groups, args.input, args.speed, args.stroke, color,
                    args.keep_colors, W, H)

    if args.out:
        with open(args.out, "w") as fh:
            fh.write(code + "\n")

    steps = total_steps(groups)
    actions = sum(len(s.pts) for g in groups for s in g)
    where = args.out if args.out else "stdout"
    if args.emit == "svg":
        print(f"[trace] {len(kept)} outlines, {actions} points -> {where}", file=sys.stderr)
    else:
        print(f"[trace] {len(kept)} outlines, {actions} actions, {steps} steps, "
              f"{len(groups)} turtles -> {where}", file=sys.stderr)
    if tol:
        print(f"[trace] simplified with a tolerance of {tol:.2f} px "
              f"to fit --max-steps {args.max_steps}", file=sys.stderr)
    if steps > 6000:
        print(f"[trace] WARNING: {steps} steps is past the stage's 6000 — "
              f"lower --max-steps or use more turtles", file=sys.stderr)
    if not args.out:
        print(code)


if __name__ == "__main__":
    main()
