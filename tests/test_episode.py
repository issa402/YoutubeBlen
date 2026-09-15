from pathlib import Path
import json
import pytest
from studio.core import Studio
from studio.episode import package, assemble


def test_package_extracts_only_narration_and_portable_scene(tmp_path):
    s = Studio(tmp_path)
    s.new('sample', 'Title', 'Take')
    source = s.episode('sample') / 'script/MASTER_PRODUCTION_SCRIPT.md'
    source.write_text('# Episode\n\n## 00:00–00:08 — Opening\n\n### Voiceover\n\nHello football.\n\n### Evidence\n\nC01 OPINION\n', encoding='utf-8')
    out = tmp_path / '.studio/packages/episode'
    result = package(s, 'sample', out)
    assert (out / 'narration.txt').read_text() == 'Hello football.\n'
    assert 'C01' not in (out / 'narration.txt').read_text()
    assert len(json.loads((out / 'shots.json').read_text())) == 1
    assert (out / 'blender/studio_scene.py').is_file()
    assert result['word_count'] == 2
    with pytest.raises(FileExistsError):
        package(s, 'sample', out)


def test_package_missing_script(tmp_path):
    s = Studio(tmp_path); s.new('sample','Title','Take')
    with pytest.raises(FileNotFoundError):
        package(s, 'sample', tmp_path / '.studio/package')


def test_package_includes_only_portable_opening_files(tmp_path):
    s = Studio(tmp_path); s.new('sample', 'Title', 'Take')
    root = s.episode('sample')
    (root / 'script/MASTER_PRODUCTION_SCRIPT.md').write_text('## Hook\n### Voiceover\nMy view.\n')
    opening = root / 'mac/opening'; opening.mkdir(parents=True)
    for name in ('opening_sequence.py', 'sequence_spec.py', 'manifest.json', 'run.sh', 'README.md', '.gitignore'):
        (opening / name).write_text('portable file')
    (opening / 'private-local.log').write_text('must not copy')
    result = package(s, 'sample', tmp_path / '.studio/export')
    assert result['opening_sequence_available']
    assert len(list((tmp_path / '.studio/export/opening').iterdir())) == 6
    assert not (tmp_path / '.studio/export/opening/private-local.log').exists()


def test_assemble_rejects_missing_sequence_bad_fps(tmp_path):
    with pytest.raises(ValueError): assemble(tmp_path, tmp_path / 'out', fps=0)
    with pytest.raises(FileNotFoundError): assemble(tmp_path, tmp_path / 'out')


def test_assemble_real_frames(tmp_path):
    import cv2
    import numpy as np
    frames = tmp_path / 'frames'; frames.mkdir()
    for i in range(1, 5):
        cv2.imwrite(str(frames / f'frame_{i:04d}.png'), np.full((64,96,3), i*30, np.uint8))
    result = assemble(frames, tmp_path / 'output', fps=4)
    assert Path(result['video']).is_file()
    assert result['frame_count'] == 4
    with pytest.raises(FileExistsError): assemble(frames, tmp_path / 'output', fps=4)
    (frames / 'frame_0002.png').unlink()
    with pytest.raises(ValueError): assemble(frames, tmp_path / 'out2', fps=4)
