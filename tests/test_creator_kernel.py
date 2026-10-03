"""State, isolation and budget regressions for the local creator workflow."""
import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from studio.core import Studio
from studio.creator_kernel import CreatorKernel, STAGES


class CreatorKernelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.studio = Studio(self.root)
        self.studio.new('episode-one', 'One', 'Preserve my point of view.')
        self.studio.new('episode-two', 'Two', 'Other episode')
        catalog = self.root / 'tools/animation-references/catalog.json'
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({'references': [{'id': 'R01', 'style': 'presenter'}]}))
        self.kernel = CreatorKernel(self.root)
        self.project = self.kernel.create_project('episode-one', 'Make my narration engaging.', ['R01'])

    def artifact(self, name='research.md'):
        path = self.root / 'episodes/episode-one' / name
        path.write_text('Actual output for review', encoding='utf-8')
        return path.relative_to(self.root).as_posix()

    def test_dependencies_and_persistence(self):
        project_id = self.project['id']
        with self.assertRaises(ValueError):
            self.kernel.prepare_handoff(project_id, 'animation')
        for stage in STAGES:
            packet = self.kernel.prepare_handoff(project_id, stage)
            self.assertTrue((self.root / packet['path']).is_file())
            result = self.kernel.complete_stage(project_id, stage, self.artifact(stage + '.md'))
            self.assertEqual(next(s for s in result['stages'] if s['stage'] == stage)['state'], 'completed')
        self.assertEqual(CreatorKernel(self.root).get_project(project_id)['state'], 'completed')

    def test_artifact_validation_and_active_scope(self):
        pid = self.project['id']
        with self.assertRaises(ValueError):
            self.kernel.complete_stage(pid, 'research', self.artifact())
        self.kernel.prepare_handoff(pid, 'research')
        for path in ('../outside.md', '.env', 'episodes/episode-two/CREATOR_TAKE.md'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.kernel.complete_stage(pid, 'research', path)
        with self.assertRaises(FileNotFoundError):
            self.kernel.complete_stage(pid, 'research', 'episodes/episode-one/missing.md')
        with self.assertRaises(ValueError):
            self.kernel.create_project('../escape', 'bad', [])
        with self.assertRaises(ValueError):
            self.kernel.create_project('episode-one', 'bad', ['R99'])

    def test_retries_are_explicit_and_bounded(self):
        pid = self.project['id']
        for attempt in range(3):
            self.kernel.prepare_handoff(pid, 'research')
            self.kernel.fail_stage(pid, 'research', 'source unavailable')
            if attempt < 2:
                self.kernel.retry_stage(pid, 'research')
        with self.assertRaises(ValueError):
            self.kernel.retry_stage(pid, 'research')

    def test_context_preserves_task_and_only_current_corrections(self):
        self.studio.feedback('episode-one', 'Use my own argument, preserve nuance.', 'voice')
        self.studio.feedback('episode-two', 'DO NOT LEAK OTHER EPISODE', 'voice')
        self.kernel.add_memory('episode-one', 'raw take', 'approved take', 'rejected take', 'Too generic')
        other = self.root / 'episodes/episode-two/research/info.md'
        other.write_text('narration engaging DO NOT LEAK SEARCH')
        self.studio.index()
        result = self.kernel.compile_context(self.project['id'], 'research', max_chars=5000)
        self.assertIn(self.project['brief'], result['context'])
        self.assertIn('Use my own argument, preserve nuance.', result['context'])
        self.assertNotIn('DO NOT LEAK', result['context'])
        self.assertLessEqual(len(result['context']), 5000)
        with self.assertRaises(ValueError):
            self.kernel.compile_context(self.project['id'], 'research', max_chars=100)

    def test_memory_is_explicit_reversible_and_episode_scoped(self):
        record = self.kernel.add_memory('episode-one', 'raw', 'yes', 'no', 'reason')
        self.assertEqual(len(self.kernel.get_memory('episode-one')), 1)
        self.assertEqual(self.kernel.get_memory('episode-two'), [])
        self.kernel.revoke_memory(record['id'])
        self.assertEqual(self.kernel.get_memory('episode-one'), [])

    def test_budget_requires_reservation_and_accounts_for_all_jobs(self):
        pid = self.project['id']
        self.kernel.prepare_handoff(pid, 'research')
        with self.assertRaises(ValueError):
            self.kernel.reserve_cost(pid, 'research', 1, 'example', 'test')
        self.kernel.set_budget(3)
        reservation = self.kernel.reserve_cost(pid, 'research', 2, 'example', 'test')
        with self.assertRaises(ValueError):
            self.kernel.reserve_cost(pid, 'research', 2, 'example', 'test')
        self.kernel.settle_cost(reservation['id'], 1.25, input_tokens=100, output_tokens=20)
        snapshot = self.kernel.dashboard_snapshot()
        self.assertEqual(snapshot['budget']['spent_usd'], 1.25)
        self.assertEqual(snapshot['budget']['remaining_usd'], 1.75)
        with self.assertRaises(ValueError):
            self.kernel.settle_cost(reservation['id'], 0)
        for invalid in (-1, float('nan'), float('inf')):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                self.kernel.set_budget(invalid)

    def test_actual_cost_overrun_is_recorded_and_blocks_new_spend(self):
        self.kernel.set_budget(1)
        self.kernel.prepare_handoff(self.project['id'], 'research')
        reservation = self.kernel.reserve_cost(self.project['id'], 'research', 1, 'x', 'y')
        self.kernel.settle_cost(reservation['id'], 2)
        self.assertTrue(self.kernel.dashboard_snapshot()['budget']['over_budget'])
        with self.assertRaises(ValueError):
            self.kernel.reserve_cost(self.project['id'], 'research', 0.01, 'x', 'y')

    def test_concurrent_reservations_cannot_exceed_cap(self):
        self.kernel.set_budget(1)
        self.kernel.prepare_handoff(self.project['id'], 'research')
        start = Barrier(2)

        def reserve():
            start.wait()
            try:
                self.kernel.reserve_cost(self.project['id'], 'research', .75, 'x', 'y')
                return True
            except ValueError:
                return False

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: reserve(), range(2)))
        self.assertEqual(sorted(outcomes), [False, True])
        self.assertEqual(self.kernel.dashboard_snapshot()['budget']['reserved_usd'], .75)

    def test_empty_artifact_and_duplicate_active_project_rejected(self):
        self.kernel.prepare_handoff(self.project['id'], 'research')
        empty = self.root / 'episodes/episode-one/empty.md'
        empty.touch()
        with self.assertRaises(ValueError):
            self.kernel.complete_stage(self.project['id'], 'research', str(empty))
        with self.assertRaises(ValueError):
            self.kernel.prepare_handoff(self.project['id'], 'research')


if __name__ == '__main__':
    unittest.main()
