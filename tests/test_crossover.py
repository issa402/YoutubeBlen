import ast
from pathlib import Path
import unittest
from blender.crossover_spec import shot_at, pose_at, FRAME_END

class CrossoverTests(unittest.TestCase):
 def test_cuts_and_duration(self):
  self.assertEqual(FRAME_END,192)
  for f,shot in ((1,'messi'),(44,'messi'),(45,'mbappe'),(87,'mbappe'),(88,'point'),(132,'point'),(133,'ronaldo'),(192,'ronaldo')):
   self.assertEqual(shot_at(f),shot)
 def test_invalid_frames(self):
  for f in (0,193,True,1.5):
   with self.assertRaises(ValueError): pose_at(f)
 def test_motion_and_reveal(self):
  self.assertEqual(pose_at(55),pose_at(55))
  self.assertLess(pose_at(88)['point_extension'],pose_at(112)['point_extension'])
  self.assertLess(pose_at(133)['reveal'],pose_at(160)['reveal'])
 def test_packet_parity(self):
  root=Path(__file__).resolve().parents[1]
  packet=root/'episodes/002-ronaldo-hate-psychology/mac/superhero-crossover'
  for name in ('superhero_crossover.py','crossover_spec.py','messi_floating.py','floating_spec.py','hd_spec.py','crossover_faces.py','crossover_sprites.py','crossover_approved.py'):
   self.assertEqual((root/'blender'/name).read_bytes(),(packet/name).read_bytes())

 def test_approved_cutout_uses_precomputed_triangles(self):
  root=Path(__file__).resolve().parents[1]
  source=(root/'blender/crossover_approved.py').read_text(encoding='utf-8')
  self.assertNotIn('tessellate_polygon',source)
  tree=ast.parse(source)
  faces=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='FACES' for target in node.targets))
  self.assertEqual(len(faces),76)
  self.assertTrue(all(len(face)==3 and all(0<=index<78 for index in face) for face in faces))
 def test_bundled_artwork_matches_packet(self):
  root=Path(__file__).resolve().parents[1]
  packet=root/'episodes/002-ronaldo-hate-psychology/mac/superhero-crossover'
  for name in ('mbappe-profile-matched.png','mbappe-crouch-matched.png','messi-omni-matched.png','ronaldo-approved.png'):
   source=(root/'blender/assets'/name).read_bytes()
   self.assertTrue(source.startswith(b'\x89PNG\r\n\x1a\n'))
   self.assertEqual(source,(packet/'assets'/name).read_bytes())
