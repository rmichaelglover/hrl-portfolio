import unittest
import numpy as np
from active import QueryOracle,policy
class QueryTests(unittest.TestCase):
 def test_budget_and_target_access(self):
  q=QueryOracle(np.arange(6),[0,1,2],budget=2)
  self.assertEqual(q.query(0),0)
  with self.assertRaises(ValueError):q.query(0)
  with self.assertRaises(ValueError):q.query(4)
  q.query(1)
  with self.assertRaises(ValueError):q.query(2)
 def test_policy_never_queries_forecast_targets(self):
  q=QueryOracle(np.arange(6)/10,[0,1,2]);p=np.eye(6)*.9+.1/6
  result=policy(p,np.zeros((6,6),int),np.zeros((3,6,6)),0,np.arange(6)/10,np.ones(6)*.1,
   np.array([0,1,2]),np.array([3,4,5]),q,np.random.default_rng(0),'disagreement')
  self.assertEqual(len(result),3);self.assertEqual(len(q.asked),2);self.assertTrue(q.asked<={0,1,2})
  self.assertTrue(all(len(pred)==3 for b,pred in result))
if __name__=='__main__':unittest.main()
