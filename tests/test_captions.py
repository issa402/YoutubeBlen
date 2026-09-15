"""Script-preserving caption alignment tests; no model download or paid calls."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import wave

import pytest

from studio import captions


def fixtures(tmp_path, text='One two three four five six seven eight nine ten.', duration=10):
    audio = tmp_path / 'voice.wav'
    with wave.open(str(audio), 'wb') as handle:
        handle.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        handle.writeframes(b'\0\0' * int(duration * 16000))
    script = tmp_path / 'script.txt'
    script.write_text(text, encoding='utf-8')
    return audio, script


def fake_asr(monkeypatch, words):
    records = [SimpleNamespace(word=text, start=start, end=end) for text, start, end in words]
    model = Mock()
    model.transcribe.return_value = (iter([SimpleNamespace(words=records)]), SimpleNamespace(language='en'))
    monkeypatch.setattr(captions, '_speech_model', lambda name: model)
    return model


def normal_words():
    return [(word, index + .05, index + .8) for index, word in enumerate(
        'one two three four five six seven eight nine ten'.split())]


def test_exact_script_and_hashes_preserved_with_asr_punctuation_errors(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path, 'ONE two, three four five six seven eight nine ten!')
    model = fake_asr(monkeypatch, normal_words())
    result = captions.align(audio, script, tmp_path / 'out')
    assert result['status'] == 'aligned'
    assert result['asr_match_ratio'] == 1
    assert result['full_spoken_word_coverage'] is True
    assert ' '.join(w['text'] for w in result['words']) == script.read_text()
    assert ' '.join(c['text'] for c in result['cues']) == script.read_text()
    assert all(w['timing_method'] == 'matched' for w in result['words'])
    assert result['source_audio_sha256'] == hashlib.sha256(audio.read_bytes()).hexdigest()
    assert result['source_text_sha256'] == hashlib.sha256(script.read_bytes()).hexdigest()
    assert Path(result['srt']).read_text().startswith('1\n00:00:00,050 -->')
    assert Path(result['vtt']).read_text().startswith('WEBVTT\n')
    assert model.transcribe.call_args.kwargs['word_timestamps'] is True
    assert 'initial_prompt' not in model.transcribe.call_args.kwargs


def test_asr_misheard_word_is_interpolated_without_changing_creator_text(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path)
    words = normal_words()
    words[4] = ('hive', 4.05, 4.8)
    fake_asr(monkeypatch, words)
    result = captions.align(audio, script, tmp_path / 'out')
    assert result['asr_match_ratio'] == .9
    assert result['words'][4]['text'] == 'five'
    assert result['words'][4]['timing_method'] == 'interpolated'
    assert result['words'][3]['end'] <= result['words'][4]['start']
    assert result['words'][4]['end'] <= result['words'][5]['start']
    assert 'hive' not in Path(result['srt']).read_text()


def test_gapless_omission_borrows_anchor_time_and_labels_every_adjusted_word(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path)
    words = [(w, float(i), float(i+1)) for i, (w, _, _) in enumerate(normal_words()) if i != 4]
    words[3] = ('four', 3.0, 5.0)
    fake_asr(monkeypatch, words)
    result = captions.align(audio, script, tmp_path / 'out')
    assert result['words'][4]['start'] < result['words'][4]['end']
    assert result['words'][3]['timing_method'] == 'interpolated'
    assert result['words'][5]['timing_method'] == 'interpolated'
    assert all(a['end'] <= b['start'] for a, b in zip(result['words'], result['words'][1:]))


def test_missing_edges_are_preserved_as_uncertain_not_dropped(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path)
    fake_asr(monkeypatch, normal_words()[1:-1])
    result = captions.align(audio, script, tmp_path / 'out')
    assert result['asr_match_ratio'] == .8
    assert [result['words'][i]['timing_method'] for i in (0, 9)] == ['interpolated', 'interpolated']
    assert result['words'][0]['start'] == 0
    assert result['words'][-1]['end'] == 10
    assert result['warnings']


def test_low_match_ratio_preserves_diagnostics_but_emits_no_subtitles(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path)
    fake_asr(monkeypatch, normal_words()[:7])
    output = tmp_path / 'out'
    with pytest.raises(ValueError, match='coverage'):
        captions.align(audio, script, output)
    report = json.loads((output / 'alignment.json').read_text())
    assert report['status'] == 'failed'
    assert report['asr_match_ratio'] == .7
    assert report['full_spoken_word_coverage'] is False
    assert len(report['asr_words']) == 7
    assert not (output / 'captions.srt').exists()


@pytest.mark.parametrize('bad', [(-1, .5), (1, 1), (1, float('nan')), (9, 11), (3, 3.5)])
def test_invalid_asr_timings_rejected_with_serializable_diagnostics(tmp_path, monkeypatch, bad):
    audio, script = fixtures(tmp_path)
    words = normal_words()
    words[1] = ('two', *bad)
    fake_asr(monkeypatch, words)
    with pytest.raises(ValueError, match='timing'):
        captions.align(audio, script, tmp_path / 'out')
    raw = (tmp_path / 'out/alignment.json').read_text()
    assert 'NaN' not in raw
    assert json.loads(raw)['status'] == 'failed'


def test_empty_recognition_fails_honestly(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path)
    fake_asr(monkeypatch, [])
    with pytest.raises(ValueError, match='coverage'):
        captions.align(audio, script, tmp_path / 'out')


def test_extra_asr_speech_is_not_hidden(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path, duration=30)
    words = normal_words() + [('unrelated', i + .05, i + .8) for i in range(10, 30)]
    fake_asr(monkeypatch, words)
    with pytest.raises(ValueError, match='coverage'):
        captions.align(audio, script, tmp_path / 'out')
    report = json.loads((tmp_path / 'out/alignment.json').read_text())
    assert report['asr_match_ratio'] == 1
    assert report['asr_precision'] < .8


def test_repeated_words_align_in_order_and_unicode_apostrophes_match(tmp_path, monkeypatch):
    text = 'You’re here and you’re here and you’re still here.'
    audio, script = fixtures(tmp_path, text)
    fake_asr(monkeypatch, [(w, i + .05, i + .8) for i, w in enumerate(
        "you're here and you're here and you're still here".split())])
    result = captions.align(audio, script, tmp_path / 'out')
    assert result['asr_match_ratio'] == 1
    assert [w['asr_index'] for w in result['words']] == list(range(9))


def test_captions_escape_formatting_without_mutating_authority_text(tmp_path, monkeypatch):
    text = r'One {\pos(0,0)} three <b>four</b> five six seven eight nine ten.'
    audio, script = fixtures(tmp_path, text)
    fake_asr(monkeypatch, [(w, i + .05, i + .8) for i, w in enumerate(text.split())])
    result = captions.align(audio, script, tmp_path / 'out')
    assert ' '.join(c['text'] for c in result['cues']) == text
    assert all('{' not in c['ass_text'] and '\\' not in c['ass_text'] for c in result['cues'])
    assert '<b>' not in Path(result['srt']).read_text()
    assert '&lt;b&gt;' in Path(result['vtt']).read_text()
    assert all(len(c['text'].split()) <= 6 for c in result['cues'])


def test_missing_or_invalid_inputs_do_not_start_model_or_create_output(tmp_path, monkeypatch):
    called = Mock()
    monkeypatch.setattr(captions, '_speech_model', called)
    audio, script = fixtures(tmp_path)
    with pytest.raises(ValueError, match='model'):
        captions.align(audio, script, tmp_path / 'out', model='remote/repo')
    with pytest.raises(FileNotFoundError):
        captions.align(tmp_path / 'missing.wav', script, tmp_path / 'out')
    script.write_text('   ')
    with pytest.raises(ValueError, match='script'):
        captions.align(audio, script, tmp_path / 'out')
    script.write_text('Normal text')
    audio.write_bytes(b'not wav')
    with pytest.raises(ValueError, match='WAV'):
        captions.align(audio, script, tmp_path / 'out')
    assert not tmp_path.joinpath('out').exists()
    called.assert_not_called()


def test_existing_output_is_never_overwritten(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path)
    output = tmp_path / 'out'
    output.mkdir()
    (output / 'alignment.json').write_text('keep')
    called = Mock()
    monkeypatch.setattr(captions, '_speech_model', called)
    with pytest.raises(FileExistsError):
        captions.align(audio, script, output)
    assert (output / 'alignment.json').read_text() == 'keep'
    called.assert_not_called()


def test_phrase_grouping_avoids_one_word_tail_and_hanging_determiner(tmp_path, monkeypatch):
    text = 'Suddenly, his failure feels like your victory.'
    audio, script = fixtures(tmp_path, text)
    fake_asr(monkeypatch, [(w, i + .05, i + .8) for i, w in enumerate(text.split())])
    result = captions.align(audio, script, tmp_path / 'out')
    assert all(2 <= len(c['text'].split()) <= 6 for c in result['cues'])
    assert all(not c['text'].endswith('your') for c in result['cues'])
    assert result['cues'][-1]['text'].endswith('your victory.')


def test_missing_cached_model_fails_without_network_and_preserves_diagnostics(tmp_path, monkeypatch):
    audio, script = fixtures(tmp_path)
    monkeypatch.setattr(captions, '_speech_model', Mock(side_effect=RuntimeError('cache unavailable')))
    with pytest.raises(ValueError, match='cache unavailable'):
        captions.align(audio, script, tmp_path / 'out')
    assert json.loads((tmp_path / 'out/alignment.json').read_text())['status'] == 'failed'
