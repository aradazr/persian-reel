#!/usr/bin/env python3
"""Tighten a talking-head clip by shortening its pauses.

Silences are capped, not deleted — a hard zero-pause cut sounds unnatural and
lands the jump on a breath. Emits the cut file plus a time map so cues authored
against the original timeline (captions, scene starts, SFX) can be moved with it.
"""
import argparse, json, re, subprocess, sys

def detect(src, noise, mind):
    out = subprocess.run(
        ['ffmpeg','-hide_banner','-i',src,'-af',f'silencedetect=noise={noise}dB:d={mind}','-vn','-f','null','-'],
        capture_output=True, text=True).stderr
    starts = [float(m) for m in re.findall(r'silence_start: ([\d.]+)', out)]
    ends   = [float(m) for m in re.findall(r'silence_end: ([\d.]+)', out)]
    return list(zip(starts, ends))[:len(ends)]

def duration(src):
    return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                                 '-of','csv=p=0',src], capture_output=True, text=True).stdout.strip())

def plan(src, noise=-32.0, mind=0.13, keep=0.06, edge=0.02):
    """keep = how much of each pause survives. edge = guard so we never clip speech."""
    total = duration(src)
    segs, cursor = [], 0.0
    for s, e in detect(src, noise, mind):
        s, e = s + edge, e - edge
        if e - s <= keep:
            continue
        cut_from = s + keep / 2
        cut_to   = e - keep / 2
        segs.append((cursor, cut_from))
        cursor = cut_to
    segs.append((cursor, total))
    segs = [(a, b) for a, b in segs if b - a > 0.02]
    tmap, t = [], 0.0
    for a, b in segs:
        tmap.append({'old_start': round(a,4), 'old_end': round(b,4), 'new_start': round(t,4)})
        t += b - a
    return segs, tmap, total, t

def render(src, segs, dst):
    parts = []
    for i,(a,b) in enumerate(segs):
        parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]")
    chain = ";".join(parts) + ";" + "".join(f"[v{i}][a{i}]" for i in range(len(segs))) \
            + f"concat=n={len(segs)}:v=1:a=1[v][a]"
    subprocess.run(['ffmpeg','-v','error','-i',src,'-filter_complex',chain,
                    '-map','[v]','-map','[a]','-c:v','libx264','-preset','medium','-crf','18',
                    '-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',
                    '-y',dst], check=True)

def remap(t, tmap):
    """Old timeline -> new. Times inside a removed pause snap to the cut point."""
    for m in tmap:
        if t < m['old_start']:
            return m['new_start']
        if t <= m['old_end']:
            return m['new_start'] + (t - m['old_start'])
    last = tmap[-1]
    return last['new_start'] + (last['old_end'] - last['old_start'])

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--map', default='timemap.json')
    ap.add_argument('--noise', type=float, default=-32.0)
    ap.add_argument('--min', type=float, default=0.13)
    ap.add_argument('--keep', type=float, default=0.06)
    a = ap.parse_args()
    segs, tmap, old, new = plan(a.src, a.noise, a.min, a.keep)
    render(a.src, segs, a.dst)
    json.dump(tmap, open(a.map,'w'), indent=1)
    print(f"{len(segs)} segments kept | {old:.2f}s -> {new:.2f}s "
          f"(cut {old-new:.2f}s, {100*(old-new)/old:.1f}%) | map -> {a.map}")
