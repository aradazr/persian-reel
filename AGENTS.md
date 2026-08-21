# persian-reel

Turn a raw Persian talking-head clip into a finished 9:16 reel: silence cut,
Whisper transcription, a cream graphics panel over the speaker, RTL captions on
the seam, hand-drawn SVG, sound effects and a music bed, rendered to MP4.

**Use this whenever someone hands over a phone or selfie video and wants it
"edited", packaged, turned into a reel, given Persian captions or subtitles,
given on-screen graphics, or wants its silences cut** — even when none of the
tooling is named.

## How to use it

Read **[`SKILL.md`](SKILL.md)** first. It carries the pipeline, the canvas
geometry, the pacing rules, and the four Persian traps that fail silently.

Then read only the reference the task needs:

| Task | File |
|---|---|
| composition HTML, framing maths, fonts, RTL scoping | [`references/composition.md`](references/composition.md) |
| sketches, icons, brand logos, catalog blocks | [`references/graphics.md`](references/graphics.md) |
| sound effects, music bed, levels, verification | [`references/audio.md`](references/audio.md) |

`scripts/` holds the working tools — run them, do not reimplement them.
`assets/composition-template.html` is a validated skeleton to start from.

## Non-negotiables

These exist because each one has already cost real debugging time:

- **Never `dir="rtl"` on `<html>`.** Preview looks perfect; the render comes out
  entirely black.
- **Never `Math.random()`.** The renderer seeks frame by frame, so every frame
  must be reproducible. Use seeded jitter.
- **Never guess audio levels.** Source files differ by 25 dB or more. Measure
  with `scripts/audiolevel.py plan`, then prove it with `verify`.
- **Never flip the footage.** Phone selfies arrive mirrored and people expect
  them that way.
- **After any structural edit, count the scenes and sample a frame from the
  middle of each.** A deleted scene leaves its CSS and its GSAP tweens behind,
  so lint passes and the panel silently renders empty.
