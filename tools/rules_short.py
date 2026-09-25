"""Local narration edit and frame-accurate finishing for Same Standard.

Source audio is never overwritten. New words use a named stock voice, not cloning.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from studio.media import ffmpeg

RATE = 48000


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, **kwargs):
    result = subprocess.run(args, capture_output=True, timeout=3600, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', 'replace')[-6000:])
    return result


def validate_edit(edit):
    if edit.get('fps') != 30 or not edit.get('clips'):
        raise ValueError('Expected a nonempty 30 fps edit')
    for c in edit['clips']:
        if c.get('scene') not in edit.get('scenes', {}):
            raise ValueError('Undefined scene')
        if c.get('kind') == 'recording':
            if not all(math.isfinite(c[v]) for v in ('in', 'out')) or not 0 <= c['in'] < c['out']:
                raise ValueError('Invalid excerpt')
        elif c.get('kind') != 'synthetic' or not isinstance(c.get('paragraph'), int) or c['paragraph'] < 1:
            raise ValueError('Invalid speech source')


def scene_rows(clips, fps):
    rows = []
    for c in clips:
        if rows and rows[-1]['id'] == c['scene']:
            rows[-1] = {**rows[-1], 'end': c['end']}
        else:
            if any(r['id'] == c['scene'] for r in rows):
                raise ValueError('Scene must be contiguous')
            rows.append(dict(id=c['scene'], start=c['start'], end=c['end']))
    if any(round(r['end'] * fps) <= round(r['start'] * fps) for r in rows):
        raise ValueError('Scene too short')
    return rows


def write_wav(path, samples):
    import numpy as np
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())


def audio(edit_path, recording, voice, output):
    import numpy as np
    edit, speech = read(edit_path), read(Path(voice) / 'timeline.json')
    validate_edit(edit)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    rows, chunks, position = [], [], 0
    for index, c in enumerate(edit['clips']):
        filters = []
        if c['kind'] == 'recording':
            source, text = recording, c['text']
            filters = [f"atrim=start={c['in']}:end={c['out']}", 'asetpts=PTS-STARTPTS']
        else:
            p = speech['paragraphs'][c['paragraph'] - 1]
            source, text = Path(voice) / p['wav'], p['text']
        filters += ['highpass=f=70', 'loudnorm=I=-18:TP=-2:LRA=9']
        result = run([ffmpeg(), '-v', 'error', '-nostdin', '-i', str(source), '-vn',
                      '-af', ','.join(filters), '-ar', str(RATE), '-ac', '1', '-f', 'f32le', 'pipe:1'])
        samples = np.frombuffer(result.stdout, dtype='<f4').copy()
        if not len(samples) or not np.isfinite(samples).all() or np.max(np.abs(samples)) < 1e-6:
            raise ValueError('Invalid or silent speech')
        if c['kind'] == 'recording' and abs(len(samples) / RATE - (c['out'] - c['in'])) > .04:
            raise ValueError('Excerpt duration mismatch')
        samples[:240] *= np.linspace(0, 1, 240)
        samples[-240:] *= np.linspace(1, 0, 240)
        gap = .11 if index < len(edit['clips']) - 1 else .6
        chunk = np.concatenate([samples, np.zeros(round(gap * RATE))])
        rows.append({**c, 'text': text, 'start': position / RATE,
                     'speech_end': (position + len(samples)) / RATE, 'end': (position + len(chunk)) / RATE})
        chunks.append(chunk)
        position += len(chunk)
    combined = np.concatenate(chunks)
    count = math.ceil(len(combined) / RATE * 30)
    combined = np.pad(combined, (0, count * 1600 - len(combined)))
    rows[-1] = {**rows[-1], 'end': len(combined) / RATE}
    scenes = scene_rows(rows, 30)
    write_wav(output / 'voiceover.wav', combined)
    effects = np.zeros(len(combined))
    rng = np.random.default_rng(20260924)
    for row in scenes:
        start = round(row['start'] * RATE)
        n = min(round(.65 * RATE), len(combined) - start)
        t = np.arange(n) / RATE
        effects[start:start+n] += .032 * np.sin(2*np.pi*(68*t-26*t*t))*np.exp(-t*10)
        effects[start:start+n] += .009 * rng.standard_normal(n)*np.sin(np.pi*t/.65)**2
    write_wav(output / 'premix.wav', combined + effects)
    run([ffmpeg(), '-v', 'error', '-nostdin', '-n', '-i', str(output / 'premix.wav'),
         '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9', '-ar', str(RATE), '-ac', '1',
         '-c:a', 'pcm_s16le', str(output / 'mix.wav')])
    (output / 'NARRATION.txt').write_text('\n\n'.join(r['text'] for r in rows)+'\n', encoding='utf-8')
    report = dict(fps=30, frame_count=count, duration_seconds=count/30, scenes=scenes, clips=rows,
                  recording_sha256=sha(recording), edit_sha256=sha(edit_path),
                  voiceover_sha256=sha(output/'voiceover.wav'), mix_sha256=sha(output/'mix.wav'),
                  voice='Supplied recording excerpts + Kokoro am_michael; no cloning',
                  recorded_excerpt_seconds=sum(c['out']-c['in'] for c in edit['clips'] if c['kind']=='recording'))
    save(output / 'timeline.json', report)
    return report


def validate_alignment(a, audio_hash, duration):
    if a.get('source_audio_sha256') != audio_hash:
        raise ValueError('Caption audio hash mismatch')
    if a.get('status') != 'aligned' or not a.get('full_spoken_word_coverage'):
        raise ValueError('Caption alignment incomplete')
    for c in a['cues']:
        if not 0 <= c['start'] < c['end'] <= duration + .01:
            raise ValueError('Caption timing out of range')


def stamp(t):
    ticks = round(t * 100)
    h, ticks = divmod(ticks, 360000)
    m, ticks = divmod(ticks, 6000)
    s, c = divmod(ticks, 100)
    return f'{h}:{m:02}:{s:02}.{c:02}'


def safe(s):
    return s.replace('\\', '／').replace('{', '（').replace('}', '）').replace('\n', r'\N')


def design(timeline, edit, aligned, path):
    header = '[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
    header += 'Style: Main,Bahnschrift,62,&H00FFFFFF,&H00FFFFFF,&H00140B08,&H90140B08,-1,0,0,0,100,100,0,0,1,3,2,5,80,80,0,1\n'
    header += 'Style: Head,Impact,104,&H00FFFFFF,&H00FFFFFF,&H00140B08,&H80140B08,0,0,0,0,100,100,0,0,1,0,2,7,80,80,0,1\n'
    header += 'Style: Label,Bahnschrift,28,&H00EDDEAF,&H00FFFFFF,&H00140B08,&H80140B08,0,0,0,0,100,100,0,0,1,0,0,7,80,80,0,1\n'
    header += '\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    events = []
    def event(s, e, text, style='Main'):
        events.append(f'Dialogue: 2,{stamp(s)},{stamp(e)},{style},,0,0,0,,{text}')
    for i, row in enumerate(timeline['scenes']):
        s, e = row['start'], row['end']
        c = edit['scenes'][row['id']]
        event(s, e, r'{\pos(82,91)}'+safe(c['chapter']), 'Label')
        event(s, e, r'{\move(45,183,80,183,0,180)\fad(80,100)}'+safe(c['headline']), 'Head')
        event(s, e, r'{\pos(83,438)\c&H58C8FF&}'+safe(c['strap']), 'Label')
        event(s, e, r'{\pos(82,1320)\fs27}'+safe(c['status']), 'Label')
        event(s, e, r'{\pos(82,1745)\fs23}'+safe(c['source']), 'Label')
        event(s, e, r'{\pos(82,1784)\fs21}ORIGINAL ANIMATION / ILLUSTRATION, NOT MATCH REPLAY', 'Label')
        length = round(900*(i+1)/len(timeline['scenes']))
        event(s, e, r'{\pos(82,128)\p1}m 0 0 l '+f'{length} 0 l {length} 4 l 0 4'+r'{\p0}', 'Label')
        if c.get('note'):
            event(s+.4, e, r'{\pos(540,1200)\fs30\fad(150,100)}'+safe(c['note']))
    for cue in aligned['cues']:
        words = aligned['words'][cue['word_start']:cue['word_end']]
        split = None
        if len(cue['text']) > 27 and len(words)>1:
            split = min(range(1,len(words)), key=lambda i: abs(len(' '.join(w['text'] for w in words[:i]))-len(' '.join(w['text'] for w in words[i:]))))
        for i,w in enumerate(words):
            text = ''
            for j,v in enumerate(words):
                text += (r'\N' if j==split else ' ' if j else '')
                text += (r'{\c&H58C8FF&}' if i==j else r'{\c&HFFFFFF&}')+safe(v['text'])
            end = words[i+1]['start'] if i+1<len(words) else cue['end']
            if end>w['start']:
                event(w['start'], min(end,timeline['duration_seconds']), r'{\pos(540,1500)\fad(20,0)}'+text)
    path.write_text(header+'\n'.join(events)+'\n', encoding='utf-8-sig')


def validate_mix(path, timeline):
    if sha(path) != timeline['mix_sha256']:
        raise ValueError('Final mix hash mismatch')
    with wave.open(str(path), 'rb') as handle:
        duration = handle.getnframes() / handle.getframerate()
    if abs(duration - timeline['duration_seconds']) > 1 / RATE:
        raise ValueError('Final mix duration mismatch')

def finish(frames, audio_dir, edit_path, alignment_path, output):
    import cv2
    t, e, a = read(audio_dir/'timeline.json'), read(edit_path), read(alignment_path)
    validate_alignment(a, sha(audio_dir/'voiceover.wav'), t['duration_seconds'])
    validate_mix(audio_dir/'mix.wav', t)
    if sha(edit_path) != t['edit_sha256']:
        raise ValueError('Edit changed after audio generation')
    expected = [frames/f'frame_{i:05}.png' for i in range(1,t['frame_count']+1)]
    if any(not p.is_file() for p in expected):
        raise ValueError('Missing rendered frames')
    im = cv2.imread(str(expected[0]))
    if im is None or im.shape[:2] != (1920,1080):
        raise ValueError('Native 1080x1920 required')
    output.mkdir(parents=True, exist_ok=False)
    design(t,e,a,output/'design.ass')
    vf='drawbox=x=0:y=0:w=iw:h=478:color=0x080d1e@0.80:t=fill,drawbox=x=0:y=1380:w=iw:h=540:color=0x080d1e@0.90:t=fill,ass=design.ass'
    run([ffmpeg(),'-v','error','-nostdin','-n','-framerate','30','-start_number','1','-i',str((frames/'frame_%05d.png').resolve()),
         '-i',str((audio_dir/'mix.wav').resolve()),'-vf',vf,'-map','0:v:0','-map','1:a:0','-frames:v',str(t['frame_count']),
         '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','same-standard.mp4'],cwd=output)
    cap = cv2.VideoCapture(str(output/'same-standard.mp4'))
    fps, count, sizes = cap.get(cv2.CAP_PROP_FPS),0,set()
    while True:
        ok, frame = cap.read()
        if not ok: break
        count += 1
        sizes.add(tuple(frame.shape[:2]))
    cap.release()
    if count != t['frame_count'] or sizes != {(1920,1080)} or abs(fps-30)>.001:
        raise ValueError('Encoded frame validation failed')
    report=dict(status='decoded',frames=count,fps=fps,duration_seconds=count/fps,width=1080,height=1920,
                video_sha256=sha(output/'same-standard.mp4'),caption_match_ratio=a['asr_match_ratio'],
                interpolated_words=a.get('interpolated_word_count'),voice=t['voice'])
    save(output/'validation.json',report)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['audio','finish'])
    for name in ('edit','recording','voice','output','frames','audio','alignment'):
        p.add_argument('--'+name,type=Path,required=name in ('edit','output'))
    a=p.parse_args()
    result=audio(a.edit,a.recording,a.voice,a.output) if a.command=='audio' else finish(a.frames,a.audio,a.edit,a.alignment,a.output)
    print(json.dumps(result,indent=2))
