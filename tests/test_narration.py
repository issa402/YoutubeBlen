import json
from pathlib import Path
import wave

import pytest

from studio.core import Studio
from studio.narration import chapter_title, create_guide, join_waves, mux_guide


def pcm(path, seconds, rate=24000):
    with wave.open(str(path), 'wb') as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(b'\0\0' * int(seconds * rate))


def test_guide_uses_actual_section_durations_and_excludes_evidence(tmp_path, monkeypatch):
    s = Studio(tmp_path)
    s.new('sample', 'Title', 'Opinion')
    (s.episode('sample') / 'script/MASTER_PRODUCTION_SCRIPT.md').write_text(
        '## Opening\n### Voiceover\nHello there.\n\nA second paragraph.\n'
        '### Evidence\nDo not narrate this.\n## Closing\n### Voiceover\nFootball.\n', encoding='utf-8')
    def synth(manifest):
        data = json.loads(Path(manifest).read_text())
        for index, item in enumerate(data['segments']):
            pcm(Path(manifest).parent / item['audio_file'], index + 1)
    monkeypatch.setattr('studio.narration.synthesize', synth)
    result = create_guide(s, 'sample', tmp_path / '.studio/voice')
    timeline = json.loads(Path(result['timeline']).read_text())
    assert result['duration_seconds'] == 6
    assert [item['start_seconds'] for item in timeline['segments']] == [0, 1, 3]
    assert [item['end_seconds'] for item in timeline['segments']] == [1, 3, 6]
    assert 'Do not narrate' not in Path(result['narration']).read_text()
    assert '00:00:03,000 --> 00:00:06,000' in Path(result['subtitles']).read_text()
    with wave.open(result['audio']) as audio:
        assert audio.getnframes() / audio.getframerate() == 6
    with pytest.raises(FileExistsError):
        create_guide(s, 'sample', tmp_path / '.studio/voice')
    assert chapter_title('00:45–01:45 — Chapter name') == 'Chapter name'


def test_opening_and_input_validation(tmp_path, monkeypatch):
    s = Studio(tmp_path); s.new('sample', 'Title', 'Take')
    with pytest.raises(FileNotFoundError):
        create_guide(s, 'sample', tmp_path / '.studio/missing', opening=True)
    (s.episode('sample') / 'script/OPENING_NARRATION.txt').write_text('My opening.')
    def synth(manifest):
        pcm(Path(manifest).parent / 'segment_0001.wav', 1)
    monkeypatch.setattr('studio.narration.synthesize', synth)
    result = create_guide(s, 'sample', tmp_path / '.studio/opening', opening=True)
    assert result['segment_count'] == 1
    assert result['synthetic_guide'] is True
    for rate in (-11, 11, 1.5):
        with pytest.raises(ValueError):
            create_guide(s, 'sample', tmp_path / '.studio/bad', rate=rate)


def test_join_rejects_incompatible_audio(tmp_path):
    pcm(tmp_path / 'a.wav', 1)
    pcm(tmp_path / 'b.wav', 1, rate=16000)
    with pytest.raises(ValueError, match='format'):
        join_waves([tmp_path / 'a.wav', tmp_path / 'b.wav'], tmp_path / 'all.wav')
    assert not (tmp_path / 'all.wav').exists()


def test_guide_does_not_silently_ignore_edited_recording_text(tmp_path, monkeypatch):
    s = Studio(tmp_path); s.new('sample', 'Title', 'Take')
    folder = s.episode('sample') / 'script'
    (folder / 'MASTER_PRODUCTION_SCRIPT.md').write_text('## Hook\n### Voiceover\nEarlier take.\n')
    (folder / 'NARRATION.txt').write_text('Creator changed this line.')
    monkeypatch.setattr('studio.narration.synthesize', lambda _: pytest.fail('Speech should not run'))
    with pytest.raises(ValueError, match='differs'):
        create_guide(s, 'sample', tmp_path / '.studio/voice')
    assert not (tmp_path / '.studio/voice').exists()


def test_mux_real_video_preserves_complete_narration(tmp_path):
    import cv2
    import numpy as np
    from studio.episode import assemble
    frames = tmp_path / 'frames'; frames.mkdir()
    for index in range(1, 5):
        cv2.imwrite(str(frames / f'frame_{index:04d}.png'), np.full((64, 96, 3), index*30, np.uint8))
    video = assemble(frames, tmp_path / 'silent', fps=4)['video']
    pcm(tmp_path / 'guide.wav', 2)
    result = mux_guide(video, tmp_path / 'guide.wav', tmp_path / 'voiced')
    cap = cv2.VideoCapture(result['video'])
    assert cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) == pytest.approx(2, abs=.1)
    cap.release()
    assert result['held_last_frame_seconds'] == 1
    with pytest.raises(FileExistsError):
        mux_guide(video, tmp_path / 'guide.wav', tmp_path / 'voiced')
