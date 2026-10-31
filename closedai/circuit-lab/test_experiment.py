import unittest
import numpy as np
from experiment import Circuit,Observation,assignment,relax,exact_map,fit_compat,fit_models,ROLES
class CircuitTests(unittest.TestCase):
 def test_reproducibility_and_no_test_truth_in_observation(self):
  a,t=Circuit(1).dataset(2);b,u=Circuit(1).dataset(2)
  np.testing.assert_array_equal(a.descriptors,b.descriptors);np.testing.assert_array_equal(t.effects,u.effects)
  self.assertFalse(hasattr(a,'labels'));self.assertFalse(hasattr(a,'effects'))
 def test_disconnected_decoy_is_causally_null(self):
  for seed in range(5):
   o,t=Circuit(seed).dataset(seed+100)
   self.assertEqual(t.effects[np.flatnonzero(t.labels==5)[0]],0)
 def test_downstream_recomputation(self):
  c=Circuit(3);x=np.ones((5,3));a,y=c.forward(x);b,z=c.forward(x,(0,0))
  self.assertTrue(np.all(b[:,0]==0));self.assertTrue(np.any(b[:,2]!=a[:,2]));self.assertTrue(np.any(y!=z))
 def test_zero_gain_preserves_unary_assignment(self):
  r=np.random.default_rng(4);p=r.uniform(.01,1,(6,6));p/=p.sum(1,keepdims=True)
  support,_,conv=relax(p,np.zeros((6,6),int),np.zeros((3,6,6)),0)
  np.testing.assert_array_equal(assignment(p),assignment(support));self.assertTrue(conv)
  np.testing.assert_allclose(support.sum(1),1,atol=1e-6);np.testing.assert_allclose(support.sum(0),1,atol=1e-6)
 def test_exact_map_zero_gain(self):
  p=np.full((6,6),.01);p[np.arange(6),np.array([4,2,5,1,0,3])]=.95
  np.testing.assert_array_equal(exact_map(p,np.zeros((6,6),int),np.zeros((3,6,6)),0),assignment(p))
 def test_label_permutation_equivariance(self):
  o,t=Circuit(30).dataset(31);compat=fit_compat([Circuit(i).dataset(i+10) for i in range(8)])
  p=np.random.default_rng(1).uniform(.1,1,(6,6));p/=p.sum(1,keepdims=True)
  result=relax(p,o.graph,compat,1)[0];perm=np.array([3,0,4,1,5,2])
  other=relax(p[perm],o.graph[np.ix_(perm,perm)],compat,1)[0]
  np.testing.assert_allclose(other,result[perm],atol=1e-6)
if __name__=='__main__':unittest.main()
