from pathlib import Path
import unittest
from blender.crossover_spec import shot_at, pose_at, FRAME_END

class CrossoverTests(unittest.TestCase):
 def test_cuts_and_duration(self):
  self.assertEqual(FRAME_END,104)
  for f,shot in ((1,'messi'),(23,'messi'),(24,'mbappe'),(46,'mbappe'),(47,'point'),(71,'point'),(72,'ronaldo'),(104,'ronaldo')):
   self.assertEqual(shot_at(f),shot)
 def test_invalid_frames(self):
  for f in (0,105,True,1.5):
   with self.assertRaises(ValueError): pose_at(f)
 def test_motion_and_reveal(self):
  self.assertEqual(pose_at(55),pose_at(55))
  self.assertLess(pose_at(47)['point_extension'],pose_at(65)['point_extension'])
  self.assertLess(pose_at(72)['reveal'],pose_at(90)['reveal'])
 def test_packet_parity(self):
  root=Path(__file__).resolve().parents[1]
  packet=root/'episodes/002-ronaldo-hate-psychology/mac/superhero-crossover'
  for name in ('superhero_crossover.py','crossover_spec.py','messi_floating.py','floating_spec.py','hd_spec.py'):
   self.assertEqual((root/'blender'/name).read_bytes(),(packet/name).read_bytes())
