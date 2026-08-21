<div align="center">

# persian-reel

**Turn a phone talking-head clip into a finished Persian Instagram Reel — automatically.**

A [Claude](https://claude.ai) skill that packages raw selfie footage with a motion-graphics
panel, RTL captions synced to speech, hand-drawn ink sketches, sound effects and a music bed,
then renders it deterministically to MP4.

![persian-reel output](docs/img/hero.png)

*Rendered by the skill's own sketch kit and icon pipeline. Speaker shown as a placeholder.*

</div>

---

## What it does

You hand Claude a `.mov` off your phone. It gives you back a finished 9:16 reel:

- **Cuts the dead air** — pauses shortened, every downstream cue re-timed automatically
- **Transcribes Persian** with Whisper large-v3 and breaks captions on natural pauses
- **Builds a graphic panel** above the speaker, changing every 3–5 seconds
- **Draws sketches** as real SVG that animate on stroke by stroke
- **Places sound** — effects on the animation beats, a music bed under the voice
- **Renders** frame-accurately through [HyperFrames](https://github.com/heygen-com/hyperframes)

Everything runs locally. Whisper, ffmpeg, the sketch kit and 5,400+ icons need no account.
Only the optional music catalogue does.

## Install

**Claude Code** — clone into your skills directory:

```bash
git clone https://github.com/USER/persian-reel ~/.claude/skills/persian-reel
```

**Claude Desktop / claude.ai** — download the packaged skill from
[Releases](../../releases) and upload it in Settings → Capabilities → Skills.

Then just talk to Claude normally:

> «این ویدیو رو برام ادیت کن» — *edit this video for me*

The skill triggers on any Persian short-form video request; you never type its name.

## Requirements

| | |
|---|---|
| Node 22+, Python 3.10+ | runtime |
| `ffmpeg` / `ffprobe` | audio and video work |
| Google Chrome | HyperFrames renders through it |
| `npm i lucide-static simple-icons` | 2,000 icons + 3,400 brand marks, offline |
| a Persian font | Peyda, Vazirmatn, or your own — **not bundled**, see [Licensing](#licensing) |

Verify with `npx hyperframes doctor`.

## The layout

A 1080×1920 canvas, split so neither half crowds the other:

| Region | Geometry |
|---|---|
| Graphic panel | `0,0 1080×920` — cream `#F7EEE7` |
| Speaker | `0,920 1080×1000` — `object-fit: cover` |
| Caption pill | centred at `top: 886` — straddles the seam |

Palette: ink `#20242F`, accent `#E07B53` for fills, `#B7502A` for anything carrying
text, pill `#3C4454`.

## The full-frame beat

![full-frame beat](docs/img/fullframe.png)

Dropping the panel and letting the speaker fill the frame is what keeps a reel from
reading as a template. Three things have to change together:

**Cut, never fade.** A crossfade shows a translucent panel sliding over moving footage —
it looks like a glitch.

**Push in about 2×.** The face goes from 0.16 of frame height to 0.32. Without it the
speaker just occupies more empty frame and the moment reads as a gap.

**Move the caption down**, or it lands on their face.

## What's inside

| Script | Does |
|---|---|
| `cutsilence.py` | shortens pauses, emits a time map so existing cues can be moved with it |
| `transcribe.py` | Whisper large-v3 → word timings → caption-sized lines |
| `sketch.py` | deterministic hand-drawn SVG — seeded jitter, never `Math.random()` |
| `icon.py` | inlines a Lucide icon at video-appropriate stroke weight |
| `brand.py` | fetches official brand marks (simple-icons → svgl) |
| `audiolevel.py` | computes `data-volume` from measured levels, then verifies the render |

Deeper docs live in `references/` — [composition](references/composition.md),
[graphics](references/graphics.md), [audio](references/audio.md).

## Four Persian traps

These cost real debugging time and none of them announce themselves.

**`<html dir="rtl">` renders a completely black video.** Preview looks perfect. Scope
`direction: rtl` to text elements in CSS instead.

**Negative `letter-spacing` closes the gaps between Persian words.** Latin headlines
tolerate tight tracking; Persian does not, because the space is the only word boundary
in a connected script. Use `letter-spacing: 0` with `word-spacing: 0.08–0.12em`.

**Persian zero «۰» is a dot.** A 300px numeral renders as a speck. Spell the number.

**Whisper's `small` model mangles Persian** — it turned «می‌شنویم» into «میشنبیم».
Use large-v3, and still proofread.

## One more thing

**Measure audio levels, never guess them.** Ten sound cues were once placed at
hand-picked volumes and nine were completely inaudible — because one file averaged
−5 dBFS and another −30.7 dBFS. A single volume number cannot serve both.
`audiolevel.py plan` solves for each, and `verify` proves the cue actually landed.

## Licensing

The code is MIT. Two things are deliberately **not** in this repo:

- **Fonts.** Peyda is commercial; bring your own licence, or use
  [Vazirmatn](https://github.com/rastikerdar/vazirmatn) (SIL OFL).
- **Brand logos.** `brand.py` fetches them on demand rather than redistributing
  trademarks. It refuses to guess when it can't find an exact match — a wrong logo
  that renders fine is worse than a missing one.

## فارسی

این یک **اسکیل برای کلاد** است که ویدیوی سلفی خام گوشی را به یک ریلز آمادهٔ اینستاگرام
تبدیل می‌کند: کات سکوت، زیرنویس فارسی سینک با گفتار، پنل گرافیکی بالای کادر،
اسکچ‌های دست‌کشیده، ساند افکت و موزیک زمینه.

نصب در Claude Code:

```bash
git clone https://github.com/USER/persian-reel ~/.claude/skills/persian-reel
```

بعد کافی است به کلاد بگویید «این ویدیو رو برام ادیت کن» — اسکیل خودش فعال می‌شود.

همه‌چیز لوکال و رایگان اجرا می‌شود؛ فقط کاتالوگ موزیک اختیاری به حساب کاربری نیاز دارد.
فونت فارسی و لوگوی برندها عمداً داخل ریپو نیستند: فونت پیدا تجاری است و لوگوها
علامت تجاری‌اند، پس `brand.py` آن‌ها را در لحظه دریافت می‌کند.

چهار تلهٔ فارسی که در بخش انگلیسی توضیح داده شده — به‌خصوص اینکه `dir="rtl"` روی تگ
`html` باعث می‌شود ویدیو **کاملاً سیاه** رندر شود در حالی که پریویو سالم است — مهم‌ترین
چیزی است که این اسکیل از شما می‌گیرد.

---

<div align="center">
Built on <a href="https://github.com/heygen-com/hyperframes">HyperFrames</a> ·
<a href="https://github.com/lucide-icons/lucide">Lucide</a> ·
<a href="https://github.com/simple-icons/simple-icons">simple-icons</a> ·
<a href="https://github.com/ggerganov/whisper.cpp">whisper.cpp</a>
</div>
