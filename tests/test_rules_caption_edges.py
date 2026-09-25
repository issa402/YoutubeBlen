import wave
import pytest
from tools.rules_short import design, validate_mix


def test_touching_phrases_do_not_overlap(tmp_path):
    a = {'words': [{'text': 'First', 'start': 0, 'end': 1},
                   {'text': 'Second', 'start': 1, 'end': 2}],
         'cues': [{'text': 'First', 'start': 0, 'end': 1, 'word_start': 0, 'word_end': 1},
                  {'text': 'Second', 'start': 1, 'end': 2, 'word_start': 1, 'word_end': 2}]}
    target = tmp_path / 'design.ass'
    design({'scenes': [], 'duration_seconds': 2}, {}, a, target)
    rows = [r.split(',') for r in target.read_text(encoding='utf-8-sig').splitlines()
            if r.startswith('Dialogue:')]
    assert rows[0][2] == rows[1][1] == '0:00:01.00'


def test_mix_identity_and_duration_are_both_required(tmp_path):
    from tools.rules_short import sha
    p = tmp_path / 'mix.wav'
    with wave.open(str(p), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b'\0\0' * 48000)
    with pytest.raises(ValueError, match='hash'):
        validate_mix(p, {'mix_sha256': 'stale', 'duration_seconds': 1})
    with pytest.raises(ValueError, match='duration'):
        validate_mix(p, {'mix_sha256': sha(p), 'duration_seconds': 2})
    validate_mix(p, {'mix_sha256': sha(p), 'duration_seconds': 1})
