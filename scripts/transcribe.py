#!/usr/bin/env python3
"""Persian transcription with word-level timings, chunked into caption-sized lines.

Uses whisper.cpp large-v3. Smaller models mangle Persian badly enough to be
unusable — `small` turned «می‌شنویم» into «میشنبیم» and «واقعیت ماجرا» into
«واقعیت مجرد». large-v3 still misses a word or two, so the output is a draft
you proofread, not final copy.
"""
import argparse, json, os, re, subprocess, sys, tempfile

MODEL = os.path.expanduser('~/.cache/hyperframes/whisper/models/ggml-large-v3.bin')

def run(src, model=MODEL, lang='fa'):
    if not os.path.exists(model):
        sys.exit(f"model missing: {model}\n"
                 f"fetch it once with:  npx hyperframes init _tmp --non-interactive "
                 f"--video {src} --language fa --model large-v3   (then delete _tmp)")
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, 'a.wav')
        subprocess.run(['ffmpeg','-v','error','-i',src,'-vn','-ar','16000','-ac','1',
                        '-c:a','pcm_s16le','-y',wav], check=True)
        out = os.path.join(td, 't')
        subprocess.run(['whisper-cli','-m',model,'-l',lang,'-f',wav,'-ojf','-of',out],
                       check=True, capture_output=True)
        return json.load(open(out + '.json'))

def words(doc):
    ws = []
    for seg in doc['transcription']:
        cur = None
        for t in seg.get('tokens', []):
            tx = t['text']
            if tx.startswith('[_'):
                continue
            if tx.startswith(' ') or cur is None:
                if cur: ws.append(cur)
                cur = {'text': tx.strip(), 'start': t['offsets']['from']/1000,
                       'end': t['offsets']['to']/1000}
            else:
                cur['text'] += tx
                cur['end'] = t['offsets']['to']/1000
        if cur: ws.append(cur)
    return ws

def chunk(ws, max_chars=34, max_gap=0.32):
    """Break on natural pauses first, length second — a caption that flips
    mid-breath reads worse than one that runs slightly long."""
    out, cur = [], []
    for w in ws:
        if cur and (w['start'] - cur[-1]['end'] > max_gap or
                    len(' '.join(x['text'] for x in cur + [w])) > max_chars):
            out.append(cur); cur = []
        cur.append(w)
    if cur: out.append(cur)
    return [{'start': round(c[0]['start'], 2), 'end': round(c[-1]['end'], 2),
             'text': ' '.join(x['text'] for x in c)} for c in out]

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('--out', default='transcript.json')
    ap.add_argument('--max-chars', type=int, default=34)
    a = ap.parse_args()
    doc = run(a.src)
    ws = words(doc)
    cs = chunk(ws, a.max_chars)
    json.dump({'words': ws, 'captions': cs}, open(a.out,'w'), ensure_ascii=False, indent=1)
    print(f"{len(ws)} words -> {len(cs)} caption lines -> {a.out}\n")
    for c in cs:
        print(f"  {c['start']:6.2f}-{c['end']:6.2f}  {c['text']}")
    print("\nProofread these — large-v3 is good on Persian but not perfect.")
