"""Deterministic hand-drawn SVG primitives — free, offline, no Math.random.

Every shape is a wobbled path: few control points (long, slow deviation like a
real marker) rather than many (which reads as a jagged badge edge). Paths carry
pathLength="1" so GSAP can draw them on with strokeDashoffset regardless of size.
"""
import math

def _rng(seed):
    s = seed & 0x7FFFFFFF
    while True:
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        yield s / 0x7FFFFFFF

def _catmull(p, close=False):
    if close:
        p = p + [p[0], p[1]]
    d = f"M {p[0][0]:.1f},{p[0][1]:.1f}"
    for i in range(len(p) - 1):
        p0 = p[i - 1] if i > 0 else p[0]
        p1, p2 = p[i], p[i + 1]
        p3 = p[i + 2] if i + 2 < len(p) else p[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d

def line(x1, y1, x2, y2, seed=1, amp=3.0, n=6):
    """A straight-ish stroke that bows the way an unruled hand line does."""
    g = _rng(seed); pts = []
    nx, ny = -(y2 - y1), (x2 - x1)
    L = math.hypot(nx, ny) or 1
    for i in range(n + 1):
        t = i / n
        j = (next(g) - 0.5) * 2 * amp * math.sin(math.pi * t)
        pts.append((x1 + (x2 - x1) * t + nx / L * j, y1 + (y2 - y1) * t + ny / L * j))
    return _catmull(pts)

def rect(x, y, w, h, seed=1, amp=3.0):
    """Four separate-feeling strokes fused into one path, corners left slightly open."""
    o = amp * 0.6
    d  = line(x - o, y, x + w + o, y, seed, amp, 5)
    d += " " + line(x + w, y - o, x + w, y + h + o, seed + 1, amp, 5)
    d += " " + line(x + w + o, y + h, x - o, y + h, seed + 2, amp, 5)
    d += " " + line(x, y + h + o, x, y - o, seed + 3, amp, 5)
    return d

def ellipse(cx, cy, rx, ry, seed=1, amp=8.0, n=13, turns=1.10, start=-0.4):
    """Marker circle: low point count = long wobbles, plus a small overshoot."""
    g = _rng(seed); pts = []
    total = int(n * turns) + 1
    for i in range(total):
        t = start + (i / n) * 2 * math.pi
        j = (next(g) - 0.5) * 2 * amp
        k = 1 + 0.015 * (i / n)
        pts.append((cx + math.cos(t) * (rx + j) * k, cy + math.sin(t) * (ry + j) * k))
    return _catmull(pts)

def poly(points, seed=1, amp=3.0, close=False):
    g = _rng(seed)
    out = [(x + (next(g) - 0.5) * 2 * amp, y + (next(g) - 0.5) * 2 * amp) for x, y in points]
    return _catmull(out, close=close)

def svg(w, h, paths, stroke="#20242F", sw=3.2):
    body = "".join(
        f'<path d="{d}" pathLength="1"{(" " + extra) if extra else ""}/>' for d, extra in paths)
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')

def edges(points, seed=1, amp=3.0, close=False, over=None):
    """Straight-edged shape: each side is its own wobbled line, so corners stay
    corners. Use this instead of poly() for desks, screens, boxes — poly()'s
    Catmull smoothing rounds them into blobs."""
    o = amp * 0.6 if over is None else over
    pts = list(points) + ([points[0]] if close else [])
    d = []
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        d.append(line(x1 - ux * o, y1 - uy * o, x2 + ux * o, y2 + uy * o, seed + i * 7, amp, 5))
    return " ".join(d)
