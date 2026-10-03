"""Worker boundaries tested offline; these tests never launch a model."""
import json
from pathlib import Path
import subprocess

import pytest

from studio.creator_worker import build_codex_command, run_worker, worker_lock


def handoff(tmp_path):
    path = tmp_path / 'handoff.md'
    path.write_text('Keep this literal $(idea) and `reference`.\nDraft a hook.', encoding='utf-8')
    return path


def test_command_uses_readonly_stdin_and_no_bypass(tmp_path):
    command = build_codex_command(['codex.exe'], tmp_path, tmp_path / 'answer.md', 'my-model')
    assert command[:2] == ['codex.exe', 'exec']
    assert command[-1] == '-'
    assert command[command.index('--sandbox') + 1] == 'read-only'
    assert command[command.index('--model') + 1] == 'my-model'
    assert '--ignore-user-config' in command
    assert not any('bypass' in arg or arg == '--approve-for-me' for arg in command)


def test_preparation_never_starts_process(tmp_path):
    result = run_worker(tmp_path, handoff(tmp_path), launcher=['missing-codex'])
    assert result['status'] == 'prepared'
    assert result['provider_called'] is False
    assert Path(result['prompt']).read_text(encoding='utf-8').endswith('Draft a hook.')
    assert Path(result['report']).is_file()
    assert not Path(result['response']).exists()


def test_execute_requires_named_model(tmp_path):
    with pytest.raises(ValueError, match='model'):
        run_worker(tmp_path, handoff(tmp_path), execute=True)


@pytest.mark.parametrize('timeout', [True, 0, 29, 1801])
def test_timeout_bounds(tmp_path, timeout):
    with pytest.raises(ValueError, match='timeout'):
        run_worker(tmp_path, handoff(tmp_path), timeout=timeout)


def test_refuses_external_handoff(tmp_path):
    root = tmp_path / 'workspace'
    root.mkdir()
    with pytest.raises(ValueError, match='workspace'):
        run_worker(root, handoff(tmp_path))


def test_concurrency_lock_is_exclusive(tmp_path):
    with worker_lock(tmp_path):
        with pytest.raises(RuntimeError, match='worker'):
            with worker_lock(tmp_path):
                pass
    assert not (tmp_path / 'worker.lock').exists()


class FakeProcess:
    def __init__(self, args, **kwargs):
        self.pid = 987654
        self.returncode = 0
        self.stdin = FakeInput()
        self.response = Path(args[args.index('--output-last-message') + 1])
        self.response.write_text('Candidate draft, not an approved fact.', encoding='utf-8')
        kwargs['stdout'].write(b'{"type":"turn.completed","usage":{"input_tokens":100,"output_tokens":20}}\n')
        kwargs['stdout'].flush()

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode


class FakeInput:
    def write(self, value):
        assert b'Keep this literal $(idea)' in value

    def close(self):
        pass


def test_opt_in_exec_preserves_unapproved_candidate_and_usage(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, 'Popen', FakeProcess)
    result = run_worker(tmp_path, handoff(tmp_path), execute=True, model='configured-model', launcher=['codex.exe'])
    assert result['status'] == 'candidate_ready'
    assert result['approved'] is False
    assert result['usage']['input_tokens'] == 100
    assert result['usage']['output_tokens'] == 20
    assert result['cost_usd'] is None
    assert Path(result['response']).is_file()
    assert json.loads(Path(result['report']).read_text())['status'] == 'candidate_ready'


def test_launch_error_preserves_report_and_releases_lock(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError('CLI is unavailable')
    monkeypatch.setattr(subprocess, 'Popen', fail)
    result = run_worker(tmp_path, handoff(tmp_path), execute=True, model='configured-model', launcher=['codex.exe'])
    assert result['status'] == 'failed'
    assert 'unavailable' in result['error']
    assert Path(result['prompt']).is_file()
    assert not (tmp_path / '.studio' / 'creator' / 'workers' / 'worker.lock').exists()
