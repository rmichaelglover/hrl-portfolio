import unittest,subprocess
import numpy as np
import experiment as e
class ExperimentChecks(unittest.TestCase):
 def test_receptors_equilibrate_and_stay_bounded(self):
  counts=e.receptor_trace(np.ones(20000),1234)
  self.assertTrue(np.all((counts>=0)&(counts<=e.N)))
  self.assertAlmostEqual(float(counts.mean()),100,delta=1)
 def test_future_does_not_change_past_forecasts(self):
  c=e.environment(12,'smooth',500);counts=e.receptor_trace(c,13)
  changed=c.copy();changed[300:]*=2
  for method in ['memoryless','filtered','predictive']:
   _,a=e.run(c,counts,method);_,b=e.run(changed,counts,method)
   np.testing.assert_array_equal([r['forecast'] for r in a[:300]],[r['forecast'] for r in b[:300]])
 def test_amount_and_transport_atp_ledger(self):
  c=e.environment(12,'smooth',500);_,rows=e.run(c,e.receptor_trace(c,13),'predictive');previous=1
  for r in rows:
   self.assertAlmostEqual(previous+r['incoming_fmol']-r['outgoing_fmol'],r['internal_amount'],places=12)
   self.assertEqual(r['atp_fmol'],r['incoming_fmol']);previous=r['internal_amount']
 def test_cpp_matches_observer_and_compartment_equations(self):
  binary=e.HERE.parents[1]/'build/receptor_prediction_demo'
  actual=np.loadtxt(subprocess.check_output([str(binary)],text=True).splitlines(),delimiter=',')
  filtered=0.;amount=1.;expected=[]
  for sensed in [1.,1.2,.8,1.5]:
   old=filtered;filtered+=(-np.expm1(-.1))*(np.log(sensed)-filtered)
   velocity=np.clip((filtered-old)/.1,-.5,.5)
   amount=amount*np.exp(-.1)+sensed*(-np.expm1(-.1))
   expected.append([sensed,np.exp(filtered),np.exp(filtered+velocity),amount])
  np.testing.assert_allclose(actual,expected,rtol=1e-13,atol=1e-14)
 def test_invalid_inputs_are_rejected(self):
  with self.assertRaises(ValueError):e.run(np.ones(500),np.ones(500)*201,'filtered')
  with self.assertRaises(ValueError):e.run(np.ones(500),np.ones(500),'mystery')
if __name__=='__main__':unittest.main()
