"""Narration-clock timeline and local HyperFrames rendering."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import wave

from .media import ffmpeg

ROOT = Path(__file__).resolve().parents[1]


def validate_timeline(plan):
    fps, frames = plan.get('fps'), plan.get('frames')
    if type(fps) is not int or fps not in (24, 25, 30, 60):
        raise ValueError('FPS must be 24, 25, 30 or 60.')
    if type(frames) is not int or not 1 <= frames <= fps * 600:
        raise ValueError('Timeline must be 1 frame to 10 minutes.')
    shots = plan.get('shots')
    if not isinstance(shots, list) or not 1 <= len(shots) <= 100:
        raise ValueError('Provide 1–100 shots.')
    cursor = 0
    for shot in shots:
        start, end = shot.get('start_frame'), shot.get('end_frame')
        if type(start) is not int or type(end) is not int or start != cursor or not start < end <= frames:
            raise ValueError('Shots must cover every frame once, without gaps.')
        if not isinstance(shot.get('caption'), str) or not 1 <= len(shot['caption']) <= 500:
            raise ValueError('Every shot needs a caption of 1–500 characters.')
        cursor = end
    if cursor != frames:
        raise ValueError('The last shot must reach the end.')
    return plan


def plan_audio(audio, captions, fps=30):
    audio = Path(audio)
    with wave.open(str(audio), 'rb') as wav:
        samples, rate = wav.getnframes(), wav.getframerate()
    frames = math.ceil(samples * fps / rate)
    if not captions or len(captions) > frames:
        raise ValueError('Need captions and at least one frame per caption.')
    shots = [dict(id=f'shot-{i+1:02}', reference_id='R04', renderer='hyperframes',
                  start_frame=i*frames//len(captions), end_frame=(i+1)*frames//len(captions), caption=caption)
             for i, caption in enumerate(captions)]
    return validate_timeline(dict(fps=fps, frames=frames, audio_samples=samples, sample_rate=rate,
                                 audio_sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),
                                 timing_method='estimated equal-duration beats; review against audio', shots=shots))


def build_composition(root, plan, output, audio=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    if not output.is_relative_to(root / '.studio'):
        raise ValueError('Composition outputs must stay in .studio.')
    validate_timeline(plan)
    if output.exists():
        raise FileExistsError('Choose a fresh composition directory.')
    library = root / 'integrations/creator/node_modules/gsap/dist/gsap.min.js'
    if not library.is_file():
        raise FileNotFoundError('Run npm ci --prefix integrations/creator --ignore-scripts.')
    if audio:
        with wave.open(str(audio), 'rb') as wav:
            frames = math.ceil(wav.getnframes()*plan['fps']/wav.getframerate())
        if frames != plan['frames']:
            raise ValueError('Narration frame count differs from timeline.')
        if plan.get('audio_sha256') and hashlib.sha256(Path(audio).read_bytes()).hexdigest() != plan['audio_sha256']:
            raise ValueError('Narration changed after timing was authored.')
    output.mkdir(parents=True)
    shutil.copyfile(library, output / 'gsap.min.js')
    if audio:
        shutil.copyfile(audio, output / 'narration.wav')
    (output / 'timeline.json').write_text(json.dumps(plan, indent=2), encoding='utf8')
    duration = plan['frames'] / plan['fps']
    captions = ''.join(f'<div class="caption" id="c{i}">{html.escape(s["caption"])}</div>' for i,s in enumerate(plan['shots']))
    cues = '\n'.join(f'tl.set("#c{i}",{{opacity:1}},{s["start_frame"]/plan["fps"]});tl.set("#c{i}",{{opacity:0}},{s["end_frame"]/plan["fps"]});' for i,s in enumerate(plan['shots']))
    template = (Path(__file__).with_name('creator_templates') / 'tactical.html').read_text(encoding='utf8')
    audio_tag = f'<audio id="narration" src="narration.wav" data-start="0" data-duration="{duration}"></audio>' if audio else ''
    for token,value in {'{{DURATION}}':str(duration),'{{FPS}}':str(plan['fps']),'{{CAPTIONS}}':captions,'{{CUES}}':cues,'{{AUDIO}}':audio_tag}.items():
        template = template.replace(token,value)
    (output / 'index.html').write_text(template, encoding='utf8')
    return dict(composition=str(output), frames=plan['frames'], duration=duration)


def render_composition(root, composition):
    root, composition = Path(root).resolve(), Path(composition).resolve()
    if not composition.is_relative_to(root / '.studio') or not (composition/'index.html').is_file():
        raise ValueError('Render only generated .studio compositions.')
    output = composition / 'final.mp4'
    if output.exists():
        raise FileExistsError('Final video already exists.')
    cli = root / 'integrations/creator/node_modules/hyperframes/bin/hyperframes.mjs'
    env = {**os.environ, 'HYPERFRAMES_NO_TELEMETRY':'1', 'DO_NOT_TRACK':'1', 'HYPERFRAMES_FFMPEG_PATH':ffmpeg()}
    bin_dir = root / '.studio/bin'
    bin_dir.mkdir(exist_ok=True)
    local_ffmpeg = bin_dir / ('ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
    if not local_ffmpeg.exists():
        shutil.copy2(ffmpeg(), local_ffmpeg)
    probe_source = root / 'integrations/creator/node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe'
    if os.name == 'nt' and probe_source.is_file():
        probe_target = bin_dir / 'ffprobe.exe'
        if not probe_target.exists():
            shutil.copy2(probe_source, probe_target)
    env['PATH'] = str(bin_dir) + os.pathsep + env.get('PATH','')
    # Use HyperFrames' pinned headless Chrome rather than an Edge installation
    # whose enterprise policy may prevent Puppeteer from launching it.
    env.pop('HYPERFRAMES_BROWSER_PATH', None)
    command = [shutil.which('node') or 'node', str(cli), 'render', str(composition), '--output', str(output), '--workers', '1', '--quality', 'draft', '--no-browser-gpu']
    with (composition/'render.log').open('w',encoding='utf8') as log:
        completed = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=1800, shell=False)
    if completed.returncode or not output.is_file():
        raise RuntimeError(f'Render failed; read {composition / "render.log"}.')
    from .media import _inspect_video
    report = _inspect_video(output)
    plan = json.loads((composition/'timeline.json').read_text(encoding='utf8'))
    if abs(report['fps']-plan['fps'])>.01 or abs(report['duration_seconds']-plan['frames']/plan['fps'])>1/plan['fps']:
        raise RuntimeError('Encoded time differs from timeline.')
    decoded = subprocess.run([ffmpeg(),'-v','error','-i',str(output),'-f','null','-'],capture_output=True,timeout=300)
    if decoded.returncode or decoded.stderr.strip():
        raise RuntimeError('Encoded video failed full decode.')
    report.update(sha256=hashlib.sha256(output.read_bytes()).hexdigest(),full_decode=True,renderer='hyperframes',provider_calls=0)
    (composition/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return dict(video=str(output),validation=report)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('plan');p.add_argument('audio',type=Path);p.add_argument('--captions',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    b=sub.add_parser('build');b.add_argument('timeline',type=Path);b.add_argument('--audio',type=Path);b.add_argument('--output',type=Path,required=True)
    r=sub.add_parser('render');r.add_argument('composition',type=Path)
    args=parser.parse_args(argv)
    if args.action=='plan':
        value=plan_audio(args.audio,[s.strip() for s in args.captions.read_text(encoding='utf8').splitlines() if s.strip()])
        with args.output.open('x',encoding='utf8') as file: json.dump(value,file,indent=2)
    elif args.action=='build': value=build_composition(ROOT,json.loads(args.timeline.read_text(encoding='utf8')),args.output,args.audio)
    else: value=render_composition(ROOT,args.composition)
    print(json.dumps(value,indent=2))


if __name__=='__main__': main()
