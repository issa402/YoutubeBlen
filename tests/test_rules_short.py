"""Meaningful timing and integrity gates for the new narration-driven short."""
import pytest
from tools.rules_short import scene_rows, validate_edit, validate_alignment


def test_scene_timing_comes_from_measured_audio_not_guessed_seconds():
    clips = [dict(scene='hook', start=0, end=3.04),
             dict(scene='hook', start=3.04, end=8.68),
             dict(scene='draw', start=8.68, end=20.4)]
    rows = scene_rows(clips, 30)
    assert rows[0] == dict(id='hook', start=0, end=8.68)
    assert rows[1] == dict(id='draw', start=8.68, end=20.4)


def test_edit_rejects_backwards_recording_and_missing_scene():
    with pytest.raises(ValueError):
        validate_edit({'fps': 30, 'scenes': {'hook': {}}, 'clips': [
            {'kind': 'recording', 'scene': 'hook', 'in': 3, 'out': 2}]})
    with pytest.raises(ValueError):
        validate_edit({'fps': 30, 'scenes': {}, 'clips': [
            {'kind': 'synthetic', 'scene': 'missing', 'paragraph': 1}]})


def test_caption_gate_rejects_wrong_audio_even_if_status_is_aligned():
    report = {'status': 'aligned', 'source_audio_sha256': 'other',
              'full_spoken_word_coverage': True, 'words': [], 'cues': []}
    with pytest.raises(ValueError, match='audio'):
        validate_alignment(report, 'expected', 4)


def test_caption_gate_rejects_cues_past_voiceover():
    report = {'status': 'aligned', 'source_audio_sha256': 'expected',
              'full_spoken_word_coverage': True, 'words': [],
              'cues': [{'start': 3, 'end': 5}]}
    with pytest.raises(ValueError, match='timing'):
        validate_alignment(report, 'expected', 4)
