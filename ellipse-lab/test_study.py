import unittest
import numpy as np
from study import canonical,curve,scene,robust,metrics,distances
class StudyTests(unittest.TestCase):
 def test_axis_swap_and_angle_wrap_preserve_geometry(self):
  p=np.array([45,54,12,31,-.2]);q=canonical(p)
  self.assertGreaterEqual(q[2],q[3]);self.assertTrue(0<=q[4]<np.pi)
  self.assertLess(np.max(distances(q,curve(p))),1e-5)
 def test_noise_free_rotated_fit_without_labels(self):
  truth=np.array([43,57,28,11,2.9]);pts=curve(truth,90)
  fit,_=robust(pts,11)
  self.assertLess(np.max(distances(fit,pts)),1e-5)
 def test_original_scene_reproduction(self):
  points,truth=scene();self.assertEqual(points.shape,(220,2))
  rng=np.random.RandomState(42);self.assertAlmostEqual(points[0,0],50+32*np.cos(np.pi/6)+rng.normal(0,.8))
 def test_original_scene_clutter_recovery(self):
  pts,truth=scene();fit,_=robust(pts,42);m=metrics(fit,truth,pts)
  self.assertLess(m['boundary_rmse'],1);self.assertGreater(m['recall'],.9)
if __name__=='__main__':unittest.main()
