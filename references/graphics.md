# Graphics

Three sources, in the order worth reaching for.

## 1. Lucide icons

2000+ line icons, ISC licensed, offline. `scripts/icon.py <name>` inlines one at
`stroke-width` 1.7 — Lucide's native 2.0 reads heavy once scaled to 90–200px.
They inherit `currentColor`, so colour them from CSS.

Text glyphs like `⌘` or `◍` are a false economy: they carry the font's own
metrics and optical weight and never sit right beside real icons.

Pass `--draw-on` to tag the paths for a stroke-on reveal.

## 2. The sketch kit

`scripts/sketch.py` generates hand-drawn SVG deterministically — seeded jitter,
never `Math.random()`, so renders stay reproducible.

```python
import sketch as S
paths = [(S.edges([(96,196),(150,196),(150,330),(96,330)], seed=79, amp=2.6, close=True), ""),
         (S.ellipse(196, 150, 36, 38, seed=97, amp=3.0, n=11), "")]
open('out.svg','w').write(S.svg(700, 520, paths, stroke="currentColor", sw=3.4))
```

Two rules that took iterations to find:

**`edges()` for anything with corners, `poly()` only for real curves.** `poly()`
smooths through its points with Catmull-Rom, which rounds a four-point desk into
an oval blob. `edges()` draws each side as its own wobbled line, so corners stay
corners.

**Few control points, not many.** `ellipse(..., n=44, amp=7)` produces a jagged
badge edge. `n=13, amp=9` produces long slow waves that read as a marker circle.
A human hand deviates slowly; high-frequency jitter reads as noise.

**Compose in side view.** In line art with no fills, overlapping shapes turn to
mush. A profile arrangement — figure left, desk right — stays legible where a
front view does not.

### Draw-on

Give paths `pathLength="1"`, then the real length stops mattering:

```css
.ink { stroke-dasharray: 1; stroke-dashoffset: 1; }
```
```javascript
tl.to("#thing .ink", { strokeDashoffset: 0, duration: 0.34,
                       stagger: 0.035, ease: "power1.inOut" }, 0.05);
```

Drawing a sketch on stroke by stroke is the one thing a raster illustration can
never do, and it is what makes the panel feel authored rather than pasted.

## 3. Catalog blocks

```bash
npx hyperframes catalog --query "wobbled boxes joined by connectors"   # English only
npx hyperframes add hw-pipeline
```

The `hw-*` family is the closest match to the marker-on-paper look. Adapting one
to a Persian portrait panel takes four edits, and the last is the dangerous one:

1. **Canvas** — `width`/`height` in CSS, `data-width`/`data-height`, the
   `viewBox`, and any hard-coded `1920` in the centring maths.
2. **Direction** — `bx = x0 + (rtl ? n-1-i : i) * (boxW + gap)`, and mirror the
   connector with a sign flip on `cx`/`ex`/`sx`/`tx`/`qx`. Arrowhead angles
   derive from the curve and need no change.
3. **Brand** — `--hw-font-print` to Peyda, `--hw-ink` (shipped light, for dark
   backgrounds) to your ink, `--hw-accent` to yours, `direction: rtl` on labels.
4. **Timing** — the sequences are written against `DUR = 7` with hard-coded step
   lengths. At any shorter duration **the last node silently falls off the end**:
   no error, no warning, it simply never appears. Derive the steps instead:

```javascript
var avail = Math.max(0.6, DUR - START - HOLD);
var U = avail / (n + (n - 1) * CONN_RATIO);
```

Always render and check the final beat of an adapted block.

## Raster illustration

Generated images work — convert ink to alpha so they sit on any background and
can be recoloured:

```python
alpha = np.clip((236 - luma) / (236 - 45), 0, 1) ** 0.85 * 255
alpha[alpha < 26] = 0        # drop paper grain, else getbbox() returns the whole frame
```

Set RGB to the ink colour, crop to `getbbox()`. Keep one locked style prompt
across a whole series or the visual language drifts between videos. Raster cannot
draw itself on, so prefer the sketch kit when the beat wants that reveal.

## 4. Brand marks

`scripts/brand.py <name>...` fetches official logos into `assets/brands/`,
alongside a `.json` with the brand's own hex colour.

```bash
python3 $S/brand.py claude openai gemini instagram   # cached after first fetch
python3 $S/brand.py cursor --print                   # straight to stdout
```

**Never redraw a logo.** A brand mark is a trademark and its exact geometry is
the whole point — an approximation looks wrong to anyone who knows the brand.
If the script finds nothing, it says so rather than guessing; ask for an official
asset instead of drawing one.

Two sources, exact matches preferred over fuzzy ones from either:

- **simple-icons** — 3400+ marks, offline, monochrome single-path, inherits
  `currentColor` so it tints to your palette. Match on title *or* slug
  (`nodedotjs` is the slug for `Node.js`).
- **svgl.app** — ~660 marks including ones simple-icons removed on legal
  request, notably **OpenAI** and **Slack**. Full colour by default; `--mono`
  flattens to `currentColor`. Needs a `User-Agent` header or it 403s.

The exactness ladder exists because substring matching silently returns the
wrong company: `openai` matched *OpenAI Gym* and `slack` matched *Slackware*.
A wrong logo that renders fine is far worse than a missing one, so exact hits
from either source win before any fuzzy hit, and a fuzzy fallback prints a
warning naming what it chose.

Useful in practice: Claude's official mark is `#D97757`, near-identical to the
warm accent this layout already uses, so it drops into the palette unchanged.
