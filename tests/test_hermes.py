from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import os
import shutil
import subprocess
import sys

import pytest

from studio.core import Studio
from studio.hermes import prepare_prompt


def sample(tmp_path):
    studio = Studio(tmp_path)
    studio.new('sample', 'Rivalry', 'Preserve my ambition and envy argument.')
    return studio


def test_handoff_includes_scoped_feedback_and_revocation(tmp_path):
    studio = sample(tmp_path)
    studio.new('other', 'Another episode', 'Unrelated take')
    feedback = studio.feedback('sample', 'Make the hook confrontational.', 'voice')
    studio.feedback('other', 'UNRELATED_FEEDBACK', 'voice')
    result = prepare_prompt(studio, 'sample', 'Draft the opening.')
    content = Path(result['path']).read_text(encoding='utf-8')
    assert 'Make the hook confrontational.' in content
    assert 'UNRELATED_FEEDBACK' not in content
    assert 'Preserve my ambition and envy argument.' in content
    assert result['characters'] == len(content)
    assert result['estimated_tokens'] == (len(content) + 3) // 4
    studio.revoke(feedback['id'])
    refreshed = prepare_prompt(studio, 'sample', 'Draft the opening.')
    assert 'Make the hook confrontational.' not in Path(refreshed['path']).read_text(encoding='utf-8')


def test_handoff_bounds_large_documents_and_preserves_task(tmp_path):
    studio = sample(tmp_path)
    episode = studio.require_episode('sample')
    (episode / 'BRIEF.md').write_text('Very long brief. ' * 20000, encoding='utf-8')
    (episode / 'CLAIMS_LEDGER.md').write_text('Claim. ' * 20000, encoding='utf-8')
    (tmp_path / 'CURRENT_STATUS.md').write_text('HISTORICAL_STATUS_SHOULD_NOT_LOAD', encoding='utf-8')
    task = 'Keep the stated opinion and create narration. ' * 30
    result = prepare_prompt(studio, 'sample', task, max_chars=5000)
    content = Path(result['path']).read_text(encoding='utf-8')
    assert len(content) <= 5000
    assert task.strip() in content
    assert 'HISTORICAL_STATUS_SHOULD_NOT_LOAD' not in content
    assert 'Never manufacture evidence' in content
    assert 'PROJECT_CONTEXT.md' in content
    assert result['truncated'] is True
    assert '[Excerpt truncated' in content


@pytest.mark.parametrize('task,budget', [('', 12000), ('x' * 4001, 12000), ('Task', 0), ('Task', 64001)])
def test_handoff_rejects_invalid_inputs(tmp_path, task, budget):
    with pytest.raises(ValueError):
        prepare_prompt(sample(tmp_path), 'sample', task, max_chars=budget)


def test_handoff_never_silently_drops_protected_feedback(tmp_path):
    studio = sample(tmp_path)
    studio.feedback('sample', 'a' * 4000, 'voice')
    studio.feedback('sample', 'b' * 4000, 'visual')
    with pytest.raises(ValueError, match='protected'):
        prepare_prompt(studio, 'sample', 'Task', max_chars=5000)
    assert not list((studio.state / 'handoffs').glob('sample-hermes-*.txt'))


def test_handoff_missing_episode_and_optional_documents(tmp_path):
    studio = sample(tmp_path)
    with pytest.raises(FileNotFoundError):
        prepare_prompt(studio, 'missing', 'Task')
    result = prepare_prompt(studio, 'sample', 'Task')
    assert result['truncated'] is False
    assert result['files_selected'] == ['episodes/sample/CREATOR_TAKE.md', 'episodes/sample/production.json']
    assert 'HERMES_HOME' not in Path(result['path']).read_text(encoding='utf-8')


def test_powershell_launcher_routes_query_file_without_provider_call(tmp_path):
    shell = shutil.which('pwsh') or shutil.which('powershell')
    if not shell:
        pytest.skip('PowerShell launcher test requires PowerShell.')
    source = (Path(__file__).resolve().parents[1] / 'hermes-studio.ps1').read_text(encoding='utf-8')
    # Stub ONLY process boundaries in a disposable copy; never invoke Hermes or authentication.
    source = source.replace('if (-not (Test-Path -LiteralPath $taskExecutable))', 'if ($false)')
    packet_path = str(tmp_path / 'folder with spaces' / 'handoff.txt')
    packet = json.dumps({'status': 'success', 'result': {'path': packet_path}}).replace("'", "''")
    generator = '$taskPromptJson = & $taskPython -m studio --root $PSScriptRoot hermes-prompt $Episode --task-file $taskInputFile --max-chars $MaxChars'
    assert generator in source
    source = source.replace(generator, f"$taskPromptJson = '{packet}'; $global:LASTEXITCODE = 0")
    invocation = '& $taskExecutable @taskInvocation'
    assert invocation in source
    source = source.replace(invocation, 'Write-Output ($taskInvocation | ConvertTo-Json -Compress); $global:LASTEXITCODE = 0')
    script = tmp_path / 'launcher.ps1'
    script.write_text(source, encoding='utf-8')
    run = subprocess.run([shell, '-NoProfile', '-File', str(script), '-Episode', 'sample',
                          '-Task', 'Use my literal $(opinion).', '--provider', 'example'],
                         capture_output=True, text=True, timeout=20, check=True)
    assert json.loads(run.stdout) == ['chat', '--query-file', packet_path, '--oneshot',
                                     '--max-turns', '20', '--provider', 'example']


def test_concurrent_handoffs_keep_each_original_task(tmp_path):
    studio = sample(tmp_path)
    tasks = [f'Unique invocation {number}: preserve this task.' for number in range(8)]
    with ThreadPoolExecutor(max_workers=4) as workers:
        results = list(workers.map(lambda task: prepare_prompt(studio, 'sample', task), tasks))
    assert len({result['path'] for result in results}) == len(tasks)
    for result, task in zip(results, tasks):
        content = Path(result['path']).read_text(encoding='utf-8')
        assert task in content
        assert sum(other in content for other in tasks) == 1


@pytest.mark.parametrize('shell_name', ['powershell', 'pwsh'])
def test_real_python_boundary_preserves_quoted_multiline_task(tmp_path, shell_name):
    shell = shutil.which(shell_name)
    if not shell:
        pytest.skip(f'{shell_name} is unavailable.')
    sample(tmp_path)
    project = Path(__file__).resolve().parents[1]
    source = (project / 'hermes-studio.ps1').read_text(encoding='utf-8')
    # Only point to this test's real Python executable; the studio CLI process is not mocked.
    source = source.replace('if (-not (Test-Path -LiteralPath $taskExecutable))', 'if ($false)')
    python_executable = sys.executable.replace("'", "''")
    source = source.replace("$taskPython = Join-Path $PSScriptRoot '.venv\\Scripts\\python.exe'",
                            f"$taskPython = '{python_executable}'")
    launcher = tmp_path / 'launcher.ps1'
    launcher.write_text(source, encoding='utf-8-sig')
    task = 'Preserve "my angle" literally.\nKeep $(opinion), `ticks`, O\'Brien and café.'
    invocation = tmp_path / 'invoke.ps1'
    task_literal = task.replace("'", "''")
    # Script-to-script binding keeps the source task literal; this isolates the PS5.1 -> Python bug.
    invocation.write_text(f"& '{launcher.as_posix()}' -Episode sample -Task '{task_literal}' -PrepareOnly\n",
                          encoding='utf-8-sig')
    environment = {**os.environ, 'PYTHONPATH': str(project), 'PYTHONIOENCODING': 'utf-8'}
    run = subprocess.run([shell, '-NoProfile', '-File', str(invocation)], env=environment,
                         capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads(run.stdout)['result']
    assert task in Path(result['path']).read_text(encoding='utf-8')
    assert not list((tmp_path / '.studio/handoffs').glob('.task-*.txt'))
