#!/usr/bin/env python3
"""Inline a Lucide icon as SVG, sized and stroked for video.

Lucide ships at 24px with stroke-width 2, which reads heavy when scaled to
90-200px on screen. Thinning to ~1.7 keeps it in the same weight family as
hand-drawn ink. Icons inherit `currentColor`, so colour them from CSS.
"""
import argparse, os, re, sys

ROOTS = ['node_modules/lucide-static/icons',
         os.path.expanduser('~/instagram/node_modules/lucide-static/icons')]

def find(name):
    for r in ROOTS:
        p = os.path.join(r, f'{name}.svg')
        if os.path.exists(p): return p
    sys.exit(f"icon '{name}' not found. install once:  npm i lucide-static")

def inline(name, sw='1.7', draw_on=False):
    s = open(find(name)).read()
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S).strip()
    s = s.replace('width="24"', 'width="100%"').replace('height="24"', 'height="100%"')
    s = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{sw}"', s)
    s = re.sub(r'\s*class="[^"]*"', '', s)
    if draw_on:   # lets GSAP stroke it on with strokeDashoffset
        s = s.replace('<path ', '<path pathLength="1" class="ink" ')
        s = s.replace('<circle ', '<circle pathLength="1" class="ink" ')
    return re.sub(r'\s+', ' ', s)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name'); ap.add_argument('--stroke', default='1.7')
    ap.add_argument('--draw-on', action='store_true')
    a = ap.parse_args()
    print(inline(a.name, a.stroke, a.draw_on))
