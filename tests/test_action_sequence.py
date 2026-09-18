"""Portable packet and source-timeline contract without importing bpy."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'episodes/002-ronaldo-hate-psychology/mac/superhero-crossover'


def test_reference_timeline_preserves_every_source_frame():
    tree = ast.parse((ROOT / 'blender/action_crossover.py').read_text(encoding='utf-8'))
    values = {}
    class ResolveConstants(ast.NodeTransformer):
        def visit_Name(self, node):
            return ast.Constant(values[node.id]) if node.id in values else node
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('FPS', 'END', 'CUTS'):
                    values[target.id] = ast.literal_eval(ResolveConstants().visit(node.value))
    assert values['FPS'] == 30 and values['END'] == 260
    cuts = values['CUTS']
    assert [frame for _, start, end in cuts for frame in range(start, end + 1)] == list(range(1, 261))
    starts = {name: start for name, start, _ in cuts}
    assert {name: starts[name] for name in ('impact cutaway', 'landing wide', 'hover', 'crouch', 'point', 'reveal')} == {
        'impact cutaway': 44, 'landing wide': 65, 'hover': 110,
        'crouch': 147, 'point': 176, 'reveal': 209}


def test_action_packet_is_self_contained_and_matches_canonical_sources():
    for name in ('action_crossover.py', 'action_motion.py', 'action_art.py', 'reference_crossover.py', 'crossover_sprites.py', 'crossover_approved.py', 'crossover_spec.py', 'hd_spec.py'):
        assert (ROOT / 'blender' / name).read_bytes() == (PACKET / name).read_bytes()
    for name in ('action-defeated.png', 'action-point-right.png', 'action-point.png', 'action-tumble.png', 'action-city.png', 'action-warehouse.png', 'reference-doorway.png'):
        data = (ROOT / 'blender/assets' / name).read_bytes()
        assert data.startswith(b'\x89PNG\r\n\x1a\n')
        assert data == (PACKET / 'assets' / name).read_bytes()
