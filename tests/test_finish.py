import hashlib
import json
from pathlib import Path
import wave

import pytest

from studio.finish import build_ass, finish, validate_alignment
from studio.media import _run, ffmpeg


def fixture(tmp_path, duration=2):
    audio, script = tmp_path / 'voice.wav', tmp_path / 'script.txt'
    script.write_text('My take. Your victory?', encoding='utf-8')
    with wave.open(str(audio), 'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(24000)
        wav.writeframes(b'\0\0' * round(duration * 24000))
    alignment = {
        'status': 'aligned', 'source_audio_sha256': hashlib.sha256(audio.read_bytes()).hexdigest(),
        'source_text_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
        'duration_seconds': duration, 'asr_match_ratio': 1.0, 'asr_precision': 1.0,
        'full_spoken_word_coverage': True,
        'cues': [{'start': 0, 'end': 1, 'text': 'My take.'},
                 {'start': 1, 'end': 2, 'text': 'Your victory?'}],
    }
    return audio, script, alignment


def test_alignment_rejects_stale_audio_text_and_changed_captions(tmp_path):
    audio, script, data = fixture(tmp_path)
    assert validate_alignment(data, audio, script) == 2
    for field in ('source_audio_sha256', 'source_text_sha256'):
        with pytest.raises(ValueError, match='fingerprint'):
            validate_alignment(data | {field: 'stale'}, audio, script)
    with pytest.raises(ValueError, match='exact narration'):
        validate_alignment(data | {'cues': data['cues'][:1]}, audio, script)
    with pytest.raises(ValueError, match='coverage'):
        validate_alignment(data | {'asr_match_ratio': .4}, audio, script)
    with pytest.raises(ValueError, match='succeeded'):
        validate_alignment(data | {'status': 'failed'}, audio, script)


@pytest.mark.parametrize('change', [
    {'duration_seconds': float('nan')}, {'duration_seconds': 3},
    {'cues': [{'start': -1, 'end': 2, 'text': 'My take. Your victory?'}]},
    {'cues': [{'start': 0, 'end': float('inf'), 'text': 'My take. Your victory?'}]},
    {'cues': [{'start': 1, 'end': 1, 'text': 'My take. Your victory?'}]},
    {'cues': []},
])
def test_invalid_timing_fails_before_output(tmp_path, change):
    audio, script, data = fixture(tmp_path)
    with pytest.raises(ValueError):
        validate_alignment(data | change, audio, script)


def test_never_cuts_long_narration_to_fit(tmp_path):
    audio, script, data = fixture(tmp_path, 30.1)
    with pytest.raises(ValueError, match='30-second'):
        validate_alignment(data, audio, script)


def test_ass_scales_to_source_and_escapes_overrides():
    data = {'cues': [{'start': 0, 'end': 2, 'text': r'{\pos(0,0)} My take.'}]}
    result = build_ass(data, 1920, 1080)
    assert 'PlayResX: 1920' in result and 'PlayResY: 1080' in result
    assert r'{\pos(0,0)}' not in result
    assert '｛＼pos(0,0)｝' in result
    assert '0:00:14.83' in result and '0:00:23.79' in result
    assert r'\pos(960,1006)' in result


def test_ass_rejects_single_token_that_would_overflow_frame():
    with pytest.raises(ValueError, match='too long'):
        build_ass({'cues': [{'start': 0, 'end': 2, 'text': 'A' * 100}]}, 1920, 1080)


def test_real_hd_finish_decodes_and_preserves_dimensions(tmp_path):
    audio, script, data = fixture(tmp_path)
    alignment = tmp_path / 'alignment.json'
    alignment.write_text(json.dumps(data), encoding='utf-8')
    source = tmp_path / 'source.mp4'
    _run([ffmpeg(), '-v', 'error', '-f', 'lavfi', '-i', 'color=c=0x12232d:s=1280x720:r=24:d=30',
          '-c:v', 'libx264', '-preset', 'ultrafast', '-threads', '2', '-pix_fmt', 'yuv420p', str(source)])
    output = tmp_path / 'finished'
    report = finish(source, audio, alignment, script, output)
    assert report['valid'] and report['picture']['decoded_frames'] == 720
    assert report['picture']['resolution'] == [1280, 720]
    assert report['picture_resized'] is False
    assert report['source_audio_seconds'] == 2
    assert report['audio']['decoded_seconds'] >= 30
    assert Path(report['poster']).is_file()
    assert (output / 'validation.json').is_file()
    with pytest.raises(FileExistsError):
        finish(source, audio, alignment, script, output)


def test_low_resolution_source_is_rejected(tmp_path):
    audio, script, data = fixture(tmp_path)
    alignment = tmp_path / 'alignment.json'
    alignment.write_text(json.dumps(data), encoding='utf-8')
    source = tmp_path / 'small.mp4'
    _run([ffmpeg(), '-v', 'error', '-f', 'lavfi', '-i', 'color=s=640x360:r=24:d=30',
          '-c:v', 'libx264', '-preset', 'ultrafast', '-threads', '2', str(source)])
    with pytest.raises(ValueError, match='HD'):
        finish(source, audio, alignment, script, tmp_path / 'rejected')
    assert not (tmp_path / 'rejected').exists()
