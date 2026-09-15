"""Convert an approved-format script to portable production files; assemble frames."""
import json
from pathlib import Path
import re
import shutil
from .core import write_json
from .render import create_package
from .media import ffmpeg, _run


def read_shots(script):
    script = Path(script)
    if not script.is_file():
        raise FileNotFoundError(f'Master production script missing: {script}')
    shots = []
    for block in re.split(r'^## ', script.read_text(encoding='utf-8-sig'), flags=re.M)[1:]:
        title, _, body = block.partition('\n')
        fields = {}
        for part in re.split(r'^### ', body, flags=re.M)[1:]:
            key, _, value = part.partition('\n')
            fields[key.strip().lower()] = value.strip()
        if fields.get('voiceover'):
            shots.append({'id': f'SH{len(shots)+1:02d}', 'section': title.strip(), **fields})
    if not shots:
        raise ValueError('Script requires ## sections with ### Voiceover blocks.')
    return shots


def package(studio, episode, output):
    base = studio.require_episode(episode)
    script = base / 'script/MASTER_PRODUCTION_SCRIPT.md'
    shots = read_shots(script)
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    narration = '\n\n'.join(s['voiceover'] for s in shots) + '\n'
    (destination / 'narration.txt').write_text(narration, encoding='utf-8')
    write_json(destination / 'shots.json', shots)
    opening = base / 'mac/opening'
    opening_files = ('opening_sequence.py', 'sequence_spec.py', 'manifest.json', 'run.sh', 'README.md', '.gitignore')
    opening_available = all((opening / name).is_file() for name in opening_files)
    if opening_available:
        (destination / 'opening').mkdir()
        for name in opening_files:
            shutil.copyfile(opening / name, destination / 'opening' / name)
    words = len(narration.split())
    record = {'episode': episode, 'word_count': words, 'estimated_minutes_at_145_wpm': round(words/145, 2),
              'scene_count': len(shots), 'narration_recorded': False, 'full_episode_rendered': False,
              'opening_sequence_available': opening_available,
              'timings': 'Section timestamps are draft targets; align shots after recording.'}
    write_json(destination / 'production-report.json', record)
    shutil.copyfile(script, destination / 'MASTER_PRODUCTION_SCRIPT.md')
    create_package(destination / 'blender', seconds=8)
    (destination / 'README.md').write_text(
        '# Episode production package\n\n'
        'narration.txt contains spoken text only; shots.json retains direction and evidence.\n'
        'Record narration first; align shot timing to that recording.\n'
        'blender/ contains a reusable eight-second rivalry scene, not a complete episode render.\n'
        'If present, opening/ contains the episode-specific three-shot, thirty-second sequence.\n'
        'Run the commands in blender/README.md on the approved Mac. Return validation.json,\n'
        'an error log and preview images for revision. Descriptions help, but images show framing.\n'
        'To assemble rendered frames on Windows: .\\studio.ps1 assemble FRAMES --output .studio/renders/SHOT --fps 24\n'
        'Optional --audio NARRATION.wav adds audio without truncating the picture.\n'
        'Source records remain in the canonical episode research folder.\n', encoding='utf-8')
    return record | {'package': str(destination)}


def assemble(frames, output, audio=None, fps=24):
    if not isinstance(fps, int) or not 1 <= fps <= 120:
        raise ValueError('FPS must be an integer from 1 to 120.')
    folder = Path(frames).resolve()
    paths = sorted(folder.glob('*.png'))
    if not paths:
        raise FileNotFoundError('No PNG frames found.')
    match = re.fullmatch(r'(.*?)(\d+)\.png', paths[0].name)
    if not match:
        raise ValueError('Frames must use a numeric sequence, for example frame_0001.png.')
    prefix, first = match.groups()
    expected = [f'{prefix}{n:0{len(first)}d}.png' for n in range(int(first), int(first)+len(paths))]
    if [p.name for p in paths] != expected:
        raise ValueError('PNG sequence has gaps or inconsistent names.')
    if audio is not None and not Path(audio).is_file():
        raise FileNotFoundError('Audio input does not exist.')
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    video = destination / 'video.mp4'
    args = [ffmpeg(), '-hide_banner', '-loglevel', 'error', '-n', '-framerate', str(fps),
            '-start_number', str(int(first)), '-i', str(folder / f'{prefix}%0{len(first)}d.png')]
    if audio is not None:
        args += ['-i', str(Path(audio).resolve()), '-map', '0:v:0', '-map', '1:a:0', '-af', 'apad', '-c:a', 'aac']
    args += ['-t', str(len(paths)/fps), '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
             '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video)]
    _run(args)
    report = {'video': str(video), 'frame_count': len(paths), 'fps': fps,
              'duration_seconds': len(paths)/fps, 'audio': str(audio) if audio else None}
    write_json(destination / 'assembly.json', report)
    return report
