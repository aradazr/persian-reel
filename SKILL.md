---
name: persian-reel
description: Build a Persian (Farsi) vertical Instagram Reel or TikTok from a talking-head clip — a cream motion-graphics panel above the speaker, burned-in RTL captions synced to speech, hand-drawn ink sketches, sound effects and a music bed — rendered deterministically to MP4 with HyperFrames. Use this whenever someone hands over a phone/selfie video and wants it "edited", "packaged", turned into a reel, given captions or subtitles in Persian, given on-screen graphics or a top panel, or wants silences cut and pacing tightened. Trigger it for any Farsi/Persian short-form vertical video work even when HyperFrames, captions, or graphics are not named explicitly.
---

# Persian Reel

Turn a raw talking-head clip into a finished 9:16 reel: the speaker holds the
lower half of the frame while a cream panel above carries the visual argument,
with Persian captions riding the seam between them.

Everything here runs locally and free. Whisper, ffmpeg, the sketch kit and the
icon set need no account; only the optional music catalog does.

## Pipeline

Run these in order. Each step's output feeds the next, and the ordering matters:
cutting silence **after** authoring means re-timing every cue by hand, so cut first.

```bash
S=~/.claude/skills/persian-reel/scripts

# 1. normalise (never flip — see "Orientation")
ffmpeg -i raw.mov -map 0:v:0 -map 0:a:0 -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -r 30 -c:a aac -b:a 192k -ac 2 -ar 48000 -movflags +faststart -y talk.mp4

# 2. tighten the pauses, before anything is timed against them
python3 $S/cutsilence.py talk.mp4 talk_cut.mp4 --map timemap.json

# 3. transcribe -> word timings + caption-sized lines (proofread the output)
python3 $S/transcribe.py talk_cut.mp4 --out transcript.json

# 4. author the composition           -> references/composition.md
# 5. graphics for each beat           -> references/graphics.md
# 6. sound                            -> references/audio.md

npm run check && npm run render
```

If a composition already exists and silence still needs cutting, `cutsilence.py`
writes a time map and `remap(t, tmap)` moves any old cue time onto the new
timeline — captions, scene starts, SFX and every GSAP cue. Remap all of them or
the video desyncs.

## Setup, once per machine

```bash
npx hyperframes init <project> --example blank --resolution portrait --non-interactive
npm i lucide-static simple-icons         # 2000+ icons + 3400+ brand marks, offline
```

Whisper's large-v3 model downloads on first `hyperframes init --model large-v3`.
Fonts, ffmpeg and Chrome are checked by `npx hyperframes doctor`.
Music is optional and needs the `heygen` CLI — see `references/audio.md`.

## Layout

A 1080×1920 canvas, split so neither half crowds the other:

| Region | Geometry |
|---|---|
| Graphic panel | `0,0 1080×920` — cream `#F7EEE7` |
| Speaker | `0,920 1080×1000` — `object-fit:cover` |
| Caption pill | centred, `top:886` — straddles the seam |

Palette: ink `#20242F`, accent `#E07B53` for fills, `#B7502A` for anything
carrying text (the lighter accent fails contrast on cream), pill `#3C4454`.

The panel need not always be on. Dropping to full-frame speaker for a beat, or
moving the panel to the bottom, keeps a long piece from feeling like a template.

**Framing.** Phone clips usually put the head around 20% down the frame, which the
panel would cover. Detect the face and set `object-position` so it lands near 38%
of the speaker region — `references/composition.md` has the arithmetic. Tell the
person to sit further back and lower in frame next time; cropping only goes so far.

## Pacing

Change the panel every 3–5 seconds. Ten scene changes across 75 seconds is the
rhythm that reads as edited rather than static; holding one graphic for eight
seconds feels broken even when it is correct.

Cut captions on natural pauses rather than fixed intervals — `transcribe.py`
already chunks on gaps, so use its lines and only merge or split where the
meaning demands it.

## Orientation

iPhone front-camera clips are usually saved mirrored. **Do not flip them.**
People are used to their mirrored face and correcting it reads as wrong to
them. If text in frame ends up backwards, mention it and let them decide.

## Persian traps

These four cost real debugging time and none of them announce themselves:

**`<html dir="rtl">` renders a completely black video.** Preview looks perfect.
Scope `direction: rtl` to the text elements in CSS instead. `npm run check`
catches this one — run it before every render.

**Negative `letter-spacing` closes the gaps between Persian words.** Latin
headlines tolerate tight tracking; Persian does not, because the space is the
only word boundary in a connected script. Use `letter-spacing: 0` with
`word-spacing: 0.08–0.12em`.

**Persian zero «۰» is a dot.** A 300px numeral renders as a speck. Spell the
number, or use a Latin digit.

**Whisper's `small` model mangles Persian.** Use large-v3 and still proofread.

## References

| Need | Read |
|---|---|
| composition HTML, framing maths, fonts, RTL scoping | `references/composition.md` |
| sketches, icons, brand logos, catalog blocks, draw-on | `references/graphics.md` |
| sound effects, music bed, levels, verification | `references/audio.md` |

`assets/composition-template.html` is a working skeleton with the panel, the
speaker, a caption pill and a registered GSAP timeline already wired.
