# Composition

## The contract

HyperFrames renders HTML through headless Chrome, frame by frame, seeking a
paused GSAP timeline. That is why every rule below exists: nothing may depend on
wall-clock time or randomness, because frame 40 must look identical whether it
is rendered first or last.

- Every timed element carries `data-start`, `data-duration`, `data-track-index`
  **and** `class="clip"`. Without the class the runtime cannot manage visibility.
- One paused timeline, registered as `window.__timelines["main"]`.
- Video is `muted playsinline`; audio rides a separate `<audio>` on the same src.
- Two clips must not overlap on one track index — give each its own track.
- No `Math.random()`, no `Date.now()`, no network fetches. Seeded jitter only.

## Fonts

Peyda for Persian. Convert the TTFs once with fontTools:

```python
from fontTools.ttLib import TTFont
f = TTFont('Peyda-Bold.ttf'); f.flavor = 'woff2'; f.save('Peyda-700.woff2')
```

Each Peyda file declares its own family name (`Peyda Black`, `Peyda Med`…), the
usual Persian packaging quirk. Collapse them under one `@font-face` family and
separate by `font-weight`; then the declared names stop mattering.

Vazirmatn is a fine open fallback (SIL OFL) if Peyda is unavailable.

## RTL without the black-screen bug

```css
body { font-family: "Peyda", sans-serif; }
.scene, .cap, .card, h1, h2 { direction: rtl; unicode-bidi: isolate; }
```

Never `dir="rtl"` on `<html>`. Chrome shapes Persian correctly either way, but
the attribute makes the render pipeline emit black frames while preview stays
fine — a silent failure that costs an hour if you do not know it.

## Framing maths

Measure the face, then place it rather than eyeballing `object-position`:

```python
import cv2
img = cv2.imread('frame.png'); h, w = img.shape[:2]
cc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
x, y, fw, fh = cc.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 5,
                                   minSize=(150, 150))[0]
face_centre = y + fh / 2                      # in source pixels
band_top = face_centre - 0.38 * 1000          # 1000 = speaker region height
print(f"object-position: 50% {100 * band_top / (h - 1000):.0f}%")
```

A 9:16 source in a half-height region is a 2× crop — you cannot show the whole
body no matter how you position it. Reference clips that fit comfortably were
shot wider, with the speaker low in frame.

## Scene structure

Group each beat in a wrapper and kill the wrapper at the boundary, so a scene
never bleeds a frame into the next:

```javascript
[["#s1-inner", 3.20, 3.45], ["#s2-inner", 5.05, 5.30]].forEach(function (e) {
  tl.to(e[0], { autoAlpha: 0, duration: 0.22, ease: "power2.in" }, e[1]);
  tl.set(e[0], { autoAlpha: 0 }, e[2]);
});
```

## The full-frame beat

Dropping the panel for a few seconds and letting the speaker fill the frame is
what keeps a long piece from reading as a template. The reference does it twice
in 75 seconds — once for about 3 s, once for the closing 20 s. Save it for a
direct-address line where the person *is* the argument; a graphic restating what
they just said is weaker than either alone.

Three things change together, and skipping any one of them makes it read as a
gap rather than emphasis:

**Cut, never fade.** The reference switches in a single frame. A 0.3 s crossfade
shows a translucent panel sliding over moving footage, which looks like a
glitch. Use `tl.set()`, not `tl.to()`, and drop any scene-exit fade scheduled
just before the cut — it only ghosts the artwork for a few frames before it is
replaced anyway.

**Push in about 2×.** Measured on the reference, the face goes from 0.164 of
frame height in panel mode to 0.319 in full-frame. Without the push-in the
speaker just occupies more empty frame.

**Move the caption down.** It would otherwise land on their face.

Animate transforms only. `npm run check` rejects tweening `top`/`height`,
because layout properties snap to whole pixels and stutter under frame-by-frame
capture. Give the speaker a full-canvas wrapper and carry all framing on the
timeline — including the resting position, so no CSS `transform` competes with
GSAP for the same property:

```javascript
tl.set("#speaker", { y: 662, scale: 1 },    0);      // panel-mode framing
tl.set("#panel",   { autoAlpha: 0 },        A);
tl.set("#speaker", { y: 0, scale: 1.28 },   A);      // push in
tl.set("#speaker", { y: 662, scale: 1 },    B);
tl.set("#panel",   { autoAlpha: 1 },        B);
```

`y: 662` reproduces `object-position: 50% 28%` in the 1000 px region — derive
yours from the framing maths above rather than copying the number.

**Check the caption against the actual footage.** The reference speaker wears
black against grey, so bare white text reads cleanly there and the pill is
dropped entirely. Against a light shirt white text disappears. Keep a slab —
a translucent one reads more cinematic than the seam pill without losing
legibility. Let the footage decide, not the template.

## Contrast

`npm run check` enforces WCAG AA. The warm accent `#E07B53` on cream measures
about 2.6:1 and fails for text — that is what `#B7502A` is for. Keep the light
accent for fills, shapes and arrowheads where contrast rules do not apply.

## Track layout that scales

| Track | Contents |
|---|---|
| 0 | speaker video |
| 1 | panel background |
| 2 | scene clips |
| 3 | captions |
| 4 | speaker audio |
| 5 | mounted catalog blocks |
| 6–7 | sound effects (alternate to avoid overlap) |
| 8 | music bed |
