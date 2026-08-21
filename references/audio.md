# Audio

## The rule that matters

**Measure levels, never guess them.** Source files differ enormously in their own
loudness. In one real pass, ten cues were placed at hand-picked volumes between
0.12 and 0.20 and nine of them were completely inaudible — because
`impact-bass-1` averages −5 dBFS while `click-soft` averages −30.7 dBFS. A single
volume number cannot serve both.

```bash
S=~/.claude/skills/persian-reel/scripts
python3 $S/audiolevel.py plan talk_cut.mp4 assets/sfx/*.mp3 assets/bgm.m4a
```

It measures each asset against the speech and prints the `data-volume` that lands
it about 8 dB under. Persian speech in these phone recordings averages ≈ −26 dBFS,
so the target is ≈ −34 dBFS.

## Sound effects

19 files ship with the `media-use` skill at
`~/.claude/skills/media-use/audio/assets/sfx/` — local, free, no account.
Copy the ones you use into the project.

Place them on animation beats, not speech beats: an icon landing, a stroke
completing, a card arriving, a CTA appearing. Under continuous narration eight
to ten cues is plenty; more turns into clutter.

Alternate two track indices so consecutive cues never overlap on one track.

```html
<audio id="sfx-hand" class="clip" src="assets/sfx/pop.mp3"
       data-start="3.52" data-duration="0.60"
       data-track-index="6" data-volume="0.407"></audio>
```

Burn effects into the file. They are frame-synced to the animation and no
platform's own audio tools can reproduce that.

## Music bed

Needs the `heygen` CLI (free tier), the one component here that wants an account:

```bash
curl -fsSL https://static.heygen.ai/cli/install.sh | bash
heygen auth login                       # the user runs this; OAuth needs a browser
export PATH="$HOME/.local/bin:$PATH"    # it installs outside the default PATH
node ~/.claude/skills/media-use/scripts/resolve.mjs \
     --type bgm --intent "<mood, instrumentation, no vocals>" --project .
```

Catalog tracks run about 31 seconds. Rather than cutting blindly from the start,
pick the steadiest window — a bed should not be mid-build under someone talking:

```python
score = seg.mean() - 0.5 * seg.std()    # over 0.1 s RMS windows, sliding
```

Then trim to length with fades, and let `data-volume` carry the level so it stays
adjustable:

```bash
ffmpeg -ss <best> -t <dur> -i bgm.wav \
  -af "afade=t=in:st=0:d=0.8,afade=t=out:st=<dur-1.2>:d=1.2" \
  -c:a aac -b:a 160k -y assets/bgm.m4a
```

## Verify by measurement

Ears are unreliable at these levels, and a cue that is 20 dB down is not "subtle",
it is absent. Diff the rendered audio against the clean speech:

```bash
python3 $S/audiolevel.py verify renders/latest.mp4 assets/video/talk_cut.mp4 \
        --cues 0.05 3.52 4.26 5.60 12.05
```

What good looks like:

| Check | Target |
|---|---|
| per-cue delta | > 0.008 RMS, or it is inaudible |
| during speech | ≈ +0.5 dB — the bed must not fight the voice |
| during pauses | ≈ +3.5 dB — it should fill the gaps |
| peak | well under 1.0 |

## Worth telling the user

A licensed track chosen inside Instagram carries no copyright risk and gets
algorithmic preference for trending audio, which a burned-in bed cannot. Offer
a second render with effects but no music so they can add their own. Sound
effects always stay burned in.
