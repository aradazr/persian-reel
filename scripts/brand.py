#!/usr/bin/env python3
"""Fetch official brand marks — never redraw them.

A brand mark is a trademark: the exact geometry is the point. Approximating one
by hand looks wrong to anyone who knows the brand and misrepresents them.

Two sources, tried in order:
  simple-icons  3400+ marks, offline once installed, one flat path + brand hex.
                Some brands (OpenAI, Slack) were removed on legal request.
  svgl.app      ~660 marks including the ones simple-icons dropped, often with
                full-colour and wordmark variants.

simple-icons paths are monochrome and inherit currentColor, so they tint to your
palette. svgl files keep their own colours — usually what you want for a logo,
but pass --mono to flatten one to currentColor.
"""
import argparse, json, os, re, subprocess, sys, time, urllib.request

CACHE = os.path.expanduser('~/instagram/assets/brands')
ALIAS = {'chatgpt': 'openai', 'gpt': 'openai', 'claudeai': 'claude',
         'vscode': 'visual studio code', 'x': 'x', 'twitter': 'x',
         'gemini': 'google gemini', 'copilot': 'github copilot'}
SVGL  = 'https://api.svgl.app'

def _si(name, exact_only=True):
    js = ('const si=require("simple-icons");'
          'const n=s=>s.toLowerCase().replace(/[^a-z0-9]/g,"");'
          'const q=n(process.argv[1]); const exact=process.argv[2]==="1";'
          'const all=Object.values(si).filter(x=>x&&x.title);'
          'const hit=all.find(i=>n(i.title)===q) || all.find(i=>i.slug&&n(i.slug)===q)'
          '  || (exact?null:all.find(i=>n(i.title).includes(q)));'
          'if(hit)console.log(JSON.stringify({title:hit.title,hex:hit.hex,path:hit.path}));')
    for cwd in (os.getcwd(), os.path.expanduser('~/instagram')):
        r = subprocess.run(['node','-e',js,name,'1' if exact_only else '0'],
                           capture_output=True, text=True, cwd=cwd)
        if r.stdout.strip():
            return json.loads(r.stdout)
    return None


def _get(url, timeout=20):
    """svgl rejects requests without a User-Agent with a 403."""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'persian-reel-skill/1.0', 'Accept': 'application/json, image/svg+xml, */*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def _svgl_index():
    """Cache the index — one fetch serves a whole batch of brands."""
    cache = os.path.join(CACHE, '.svgl-index.json')
    if os.path.exists(cache) and (time.time() - os.path.getmtime(cache)) < 7 * 86400:
        return json.load(open(cache))
    data = json.loads(_get(SVGL))
    os.makedirs(CACHE, exist_ok=True)
    json.dump(data, open(cache, 'w'))
    return data

def _svgl(name, exact_only=True):
    data = _svgl_index()
    norm = lambda t: re.sub(r'[^a-z0-9]', '', t.lower())
    q = norm(name)
    hit = next((x for x in data if norm(x['title']) == q), None)
    if hit is None and not exact_only:
        hit = next((x for x in data if q in norm(x['title'])), None)
    if not hit:
        return None
    route = hit['route']
    url = route if isinstance(route, str) else route.get('light') or next(iter(route.values()))
    return {'title': hit['title'], 'svg': _get(url).decode('utf-8'), 'source': 'svgl'}


def fetch(name, mono=False, out_dir=CACHE):
    os.makedirs(out_dir, exist_ok=True)
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    query = ALIAS.get(re.sub(r'[^a-z0-9]', '', name.lower()), name)
    hit = _si(query, exact_only=True)
    svg_hit = None
    if hit is None:
        svg_hit = _svgl(query, exact_only=True)
    if hit is None and svg_hit is None:
        hit = _si(query, exact_only=False)
        if hit:
            print(f"  ! '{name}' had no exact match; using '{hit['title']}' — verify it",
                  file=sys.stderr)
    if hit:
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
               f'fill="currentColor" role="img" aria-label="{hit["title"]}">'
               f'<path d="{hit["path"]}"/></svg>')
        meta = {'title': hit['title'], 'hex': '#' + hit['hex'], 'source': 'simple-icons',
                'mono': True}
    else:
        s = svg_hit or _svgl(query, exact_only=False)
        if not s:
            sys.exit(f"no official mark found for '{name}' — do not redraw it; "
                     f"ask the user for an official asset")
        svg = s['svg']
        if mono:
            svg = re.sub(r'fill="(?!none)[^"]*"', 'fill="currentColor"', svg)
            svg = re.sub(r'stop-color="[^"]*"', 'stop-color="currentColor"', svg)
        meta = {'title': s['title'], 'source': 'svgl', 'mono': mono}
    svg = re.sub(r'\s+', ' ', svg).strip()
    path = os.path.join(out_dir, f'{slug}.svg')
    open(path, 'w').write(svg)
    meta['path'] = path
    json.dump(meta, open(os.path.join(out_dir, f'{slug}.json'), 'w'), indent=1)
    return meta

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='+')
    ap.add_argument('--mono', action='store_true', help='flatten svgl colours to currentColor')
    ap.add_argument('--out', default=CACHE)
    ap.add_argument('--print', action='store_true', help='emit the SVG to stdout')
    a = ap.parse_args()
    for n in a.names:
        m = fetch(n, a.mono, a.out)
        if a.print:
            print(open(m['path']).read())
        else:
            print(f"{m['title']:22s} {m['source']:14s} {m.get('hex',''):8s} -> {m['path']}")
