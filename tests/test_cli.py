"""Exercise the public CLI against isolated real filesystem/database state."""
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pytest
from studio.__main__ import main
from studio.core import Studio


def invoke(root, capsys, *args, code=0):
    assert main(['--root', str(root), *args]) == code
    return json.loads(capsys.readouterr().out)


def test_creator_workflow_through_cli(tmp_path, capsys):
    invoke(tmp_path, capsys, 'new', 'sample', '--title', 'Rivalry', '--take', 'Keep my original thesis')
    feedback = invoke(tmp_path, capsys, 'feedback', 'sample', 'Keep punchy sentences')['result']
    context = invoke(tmp_path, capsys, 'context', 'sample')['result']
    assert 'Keep my original thesis' in context and 'Keep punchy sentences' in context
    saved = invoke(tmp_path, capsys, 'context', 'sample', '--save')['result']['path']
    assert Path(saved).read_text(encoding='utf-8') == context
    invoke(tmp_path, capsys, 'index')
    assert invoke(tmp_path, capsys, 'search', 'original thesis')['result']
    invoke(tmp_path, capsys, 'metrics', 'sample', '--impressions', '100', '--ctr', '6',
           '--retention30', '70', '--hours', '4', '--cost', '0')
    invoke(tmp_path, capsys, 'enqueue', 'dashboard')
    assert invoke(tmp_path, capsys, 'run-next')['result']['status'] == 'success'
    assert invoke(tmp_path, capsys, 'jobs')['result'][0]['state'] == 'completed'
    assert Path(invoke(tmp_path, capsys, 'dashboard')['result']['path']).exists()
    invoke(tmp_path, capsys, 'revoke', feedback['id'])
    assert invoke(tmp_path, capsys, 'learn')['result'][0]['active'] == 0


def test_cli_error_contract_and_file_take(tmp_path, capsys):
    take = tmp_path / 'take.txt'
    take.write_text('Human voice', encoding='utf-8-sig')
    invoke(tmp_path, capsys, 'new', 'sample', '--title', 'Title', '--take-file', str(take))
    assert invoke(tmp_path, capsys, 'context', 'missing', code=1)['status'] == 'error'
    invoke(tmp_path, capsys, 'enqueue', 'index', '--args', '[]', code=1)
    invoke(tmp_path, capsys, 'enqueue', 'index', '--args', 'broken', code=1)
    invoke(tmp_path, capsys, 'render-package', '--output', '../escape', code=1)
    invoke(tmp_path, capsys, 'render-package', '--output', '.studio/packages/test', '--seconds', '2')
    assert (tmp_path / '.studio/packages/test/manifest.json').exists()


def test_failed_job_retry_limit_and_error_exit(tmp_path, capsys):
    job = invoke(tmp_path, capsys, 'enqueue', 'prepare', '--args',
                 json.dumps({'input': str(tmp_path / 'missing.mp4'), 'output': '.studio/media/test'}))['result']
    for attempt in range(3):
        assert invoke(tmp_path, capsys, 'run-next', code=1)['result']['status'] == 'error'
        if attempt < 2:
            invoke(tmp_path, capsys, 'retry', job['id'])
    invoke(tmp_path, capsys, 'retry', job['id'], code=1)
    assert Studio(tmp_path).jobs()[0]['attempts'] == 3


def test_live_job_cannot_be_requeued(tmp_path):
    studio = Studio(tmp_path)
    job = studio.enqueue('index', {})
    with studio.db() as db:
        db.execute("UPDATE jobs SET state='running', attempts=1 WHERE id=?", (job['id'],))
    with pytest.raises(ValueError):
        studio.retry(job['id'])


def test_database_context_closes_connection(tmp_path):
    with Studio(tmp_path).db() as connection:
        assert connection.execute('SELECT 1').fetchone()[0] == 1
    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute('SELECT 1')


def test_two_workers_claim_job_once(tmp_path):
    studio = Studio(tmp_path)
    studio.enqueue('index', {})
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: studio.run_next(), range(2)))
    assert sorted(r['status'] for r in results) == ['idle', 'success']
    assert studio.jobs()[0]['attempts'] == 1


def test_doctor_and_source_cli(tmp_path, capsys):
    result = invoke(tmp_path, capsys, 'doctor')['result']
    assert result['python'] and result['ffmpeg']
    assert result['learning'] == 'explicit feedback retrieval; no model retraining'
    invoke(tmp_path, capsys, 'new', 'sample', '--title', 'Title', '--take', 'Take')
    source = invoke(tmp_path, capsys, 'source', 'sample', '--url', 'https://example.com/article',
                    '--title', 'An article', '--published', '2026-09-05', '--event-date', '2022-12-18')['result']
    assert source['event_date'] == '2022-12-18'
    assert source['publication_date'] == '2026-09-05'


def test_queued_render_package_is_portable(tmp_path, capsys):
    invoke(tmp_path, capsys, 'enqueue', 'render-package', '--args',
           json.dumps({'output': '.studio/packages/queued', 'seconds': 3}))
    result = invoke(tmp_path, capsys, 'run-next')['result']
    assert result['status'] == 'success'
    manifest = json.loads((tmp_path / '.studio/packages/queued/manifest.json').read_text())
    assert manifest['frame_end'] == 72 and manifest['output'] == 'frames'
    assert (tmp_path / '.studio/packages/queued/studio_scene.py').exists()


def test_hermes_handoff_preserves_correction_and_revocation(tmp_path, capsys):
    invoke(tmp_path, capsys, 'new', 'sample', '--title', 'Title', '--take', 'My opinion')
    correction = invoke(tmp_path, capsys, 'feedback', 'sample', 'Keep the specific creator view')['result']
    result = invoke(tmp_path, capsys, 'hermes-prompt', 'sample', '--task', 'Tighten the hook')['result']
    text = Path(result['path']).read_text(encoding='utf-8')
    assert 'Tighten the hook' in text and 'Keep the specific creator view' in text
    assert result['characters'] <= 12000
    invoke(tmp_path, capsys, 'revoke', correction['id'])
    again = invoke(tmp_path, capsys, 'hermes-prompt', 'sample', '--task', 'Tighten the hook')['result']
    assert 'Keep the specific creator view' not in Path(again['path']).read_text(encoding='utf-8')


def test_review_cli_exports_local_work_without_claiming_completion(tmp_path, capsys):
    invoke(tmp_path, capsys, 'new', 'sample', '--title', 'Title', '--take', 'Creator take')
    result = invoke(tmp_path, capsys, 'review', 'sample', '--output', '.studio/reviews/first')['result']
    assert result['summary']['chapter_count'] == 0
    assert (Path(result['output']) / 'edit-timeline.csv').is_file()
    invoke(tmp_path, capsys, 'review', 'sample', '--output', '.studio/reviews/first', code=1)
    invoke(tmp_path, capsys, 'review', 'sample', '--output', '../outside', code=1)


def test_caption_and_finish_cli_forward_scoped_inputs(tmp_path, capsys, monkeypatch):
    def alignment(audio, text, output, model):
        assert audio == Path('voice.wav') and text == Path('script.txt') and model == 'tiny'
        assert output == tmp_path / '.studio/captions/test'
        return {'status': 'aligned'}
    monkeypatch.setattr('studio.captions.align', alignment)
    result = invoke(tmp_path, capsys, 'align-captions', 'voice.wav', '--text', 'script.txt',
                    '--output', '.studio/captions/test')
    assert result['result']['status'] == 'aligned'
    def finishing(video, audio, alignment, text, output):
        assert [video, audio, alignment, text] == list(map(Path, ['video.mp4', 'voice.wav', 'alignment.json', 'script.txt']))
        assert output == tmp_path / '.studio/renders/test'
        return {'valid': True}
    monkeypatch.setattr('studio.finish.finish', finishing)
    assert invoke(tmp_path, capsys, 'finish-opening', 'video.mp4', '--audio', 'voice.wav',
                  '--alignment', 'alignment.json', '--text', 'script.txt',
                  '--output', '.studio/renders/test')['result']['valid']
