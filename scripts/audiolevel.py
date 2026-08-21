#!/usr/bin/env python3
"""Set and verify audio levels by measurement instead of guesswork.

Guessing `data-volume` fails badly because source files differ enormously in
their own loudness — in one real case `impact-bass-1` averaged -5 dBFS while
`click-soft` averaged -30.7 dBFS. A single volume number applied to both made
one deafening and the other silent. So: measure each file, measure the speech,
and solve for the gain that lands the cue where you want it.

  plan   — print data-volume for each asset against the speech track
  verify — prove each cue actually changed the rendered audio
"""
import argparse, json, re, subprocess, sys
import numpy as np

def mean_db(path):
    out = subprocess.run(['ffmpeg','-hide_banner','-i',path,'-af','volumedetect','-vn','-f','null','-'],
                         capture_output=True, text=True).stderr
    m = re.search(r'mean_volume:\s*(-?[\d.]+) dB', out)
    return float(m.group(1)) if m else None

def envelope(path, hz=10):
    w = 8000 // hz
    raw = subprocess.run(['ffmpeg','-v','error','-i',path,'-ac','1','-ar','8000','-f','s16le','-'],
                         capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    n = len(a) // w
    return np.sqrt((a[:n*w].reshape(n, w) ** 2).mean(axis=1))

def plan(speech, assets, target_offset=-8.0):
    sp = mean_db(speech)
    print(f"speech mean {sp:.1f} dBFS   target for beds/cues: {sp+target_offset:.1f} dBFS\n")
    print(f"{'asset':22s}{'mean dBFS':>11s}{'data-volume':>13s}")
    for p in assets:
        m = mean_db(p)
        v = round(10 ** (((sp + target_offset) - m) / 20), 3)
        print(f"{p.split('/')[-1]:22s}{m:11.1f}{min(v,1.0):13.3f}")
    print("\nBGM sits at the same target; SFX accents may go ~4 dB hotter.")

def verify(rendered, clean, cues=None):
    r, o = envelope(rendered), envelope(clean)
    n = min(len(r), len(o)); d = r[:n] - o[:n]
    db = lambda x: 20*np.log10(max(float(x), 1e-6))
    if cues:
        print(f"{'cue':>8s}{'delta':>9s}   audible?")
        for t in cues:
            i = int(float(t)*10); j = min(i+7, n)
            dl = d[i:j].max()
            print(f"{float(t):8.2f}{dl:+9.4f}   {'yes' if dl > 0.008 else 'NO — raise it'}")
    thr = np.percentile(o[:n], 55); sp = o[:n] > thr
    print(f"\nduring speech {db(r[:n][sp].mean())-db(o[:n][sp].mean()):+5.1f} dB   "
          f"(want ~+0.5 — a bed must not fight the voice)")
    print(f"during pauses {db(r[:n][~sp].mean())-db(o[:n][~sp].mean()):+5.1f} dB   "
          f"(want ~+3.5 — it should fill the gaps)")
    print(f"peak {r.max():.3f}   (clipping at 1.0)")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p1 = sub.add_parser('plan');   p1.add_argument('speech'); p1.add_argument('assets', nargs='+')
    p2 = sub.add_parser('verify'); p2.add_argument('rendered'); p2.add_argument('clean')
    p2.add_argument('--cues', nargs='*', default=[])
    a = ap.parse_args()
    plan(a.speech, a.assets) if a.cmd == 'plan' else verify(a.rendered, a.clean, a.cues)
