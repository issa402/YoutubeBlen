"""Editorial overlays must preserve narration, timing, picture, and source files."""
import json
from pathlib import Path
import subprocess

import imageio_ffmpeg
import pytest

from blender.polish_opening import caption_cues, build_ass, validate_timeline, polish


def sample_timeline():
    return {
        'synthetic_guide': True,
        'duration_seconds': 29.793,
        'segments': [
            {'text': 'Imagine this. Messi has just done something brilliant.',
             'start_seconds': 0, 'end_seconds': 10.0},
            {'text': 'My take is that, for some fans, Ronaldo is an uncomfortable package.',
             'start_seconds': 10.0, 'end_seconds': 29.793},
        ],
    }


def test_captions_preserve_every_word_within_measured_paragraphs():
    timeline = sample_timeline()
    cues = caption_cues(timeline)
    assert ' '.join(c['text'] for c in cues) == ' '.join(s['text'] for s in timeline['segments'])
    assert cues[0]['start'] == 0
    assert cues[-1]['end'] == 29.793
    assert all(c['start'] < c['end'] and len(c['text'].split()) <= 7 for c in cues)
    assert all(a['end'] <= b['start'] for a, b in zip(cues, cues[1:]))
    assert all(c['timing'] == 'approximate within measured paragraph' for c in cues)


@pytest.mark.parametrize('mutation', [
    lambda t: t.update(duration_seconds=31),
    lambda t: t['segments'][0].update(end_seconds=float('nan')),
    lambda t: t['segments'][0].update(text=''),
    lambda t: t['segments'][1].update(start_seconds=9),
    lambda t: t['segments'][-1].update(end_seconds=29),
    lambda t: t.update(segments=[]),
])
def test_bad_timeline_rejected(mutation):
    timeline = sample_timeline()
    mutation(timeline)
    with pytest.raises(ValueError):
        validate_timeline(timeline)


def test_ass_keeps_overlays_outside_full_picture_and_escapes_instructions():
    timeline = sample_timeline()
    timeline['segments'][0]['text'] = r'This {\pos(0,0)} is literal.'
    ass = build_ass(timeline)
    assert 'PlayResX: 1280' in ass
    assert 'PlayResY: 720' in ass
    assert r'\pos(640,683)' in ass
    assert r'This {\pos(0,0)}' not in ass
    assert '01 / THE RIVAL' in ass
    assert '02 / THE WHOLE PACKAGE' in ass
    assert '03 / YOUR VICTORY?' in ass
    assert 'SYNTHETIC GUIDE' in ass


def test_existing_output_preserved(tmp_path):
    output = tmp_path / 'result'
    output.mkdir()
    sentinel = output / 'keep.txt'
    sentinel.write_text('unchanged')
    with pytest.raises(FileExistsError):
        polish(tmp_path / 'input.mp4', tmp_path / 'timeline.json', output)
    assert sentinel.read_text() == 'unchanged'


def test_real_video_audio_and_complete_picture_survive_export(tmp_path):
    source = tmp_path / 'source.mp4'
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-n',
        '-f', 'lavfi', '-i', 'color=c=navy:s=96x54:r=24:d=30',
        '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=24000:duration=30',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-c:a', 'aac', str(source),
    ], check=True)
    timeline = tmp_path / 'timeline.json'
    timeline.write_text(json.dumps(sample_timeline()), encoding='utf-8')
    output = tmp_path / 'output'
    before = source.read_bytes()
    report = polish(source, timeline, output)
    assert report['valid']
    assert report['picture'] == {'decoded_frames': 720, 'fps': 24.0,
                                 'duration_seconds': 30.0, 'resolution': [1280, 720]}
    assert report['audio_preserved_bitexact_after_decode']
    assert report['audio']['decoded_seconds'] >= 29.793
    assert report['picture_box_xywh'] == (96, 42, 1088, 612)
    assert report['upscaled'] and report['synthetic_guide']
    assert (output / 'poster.png').is_file()
    assert (output / 'frame-0720.png').is_file()
    assert source.read_bytes() == before
