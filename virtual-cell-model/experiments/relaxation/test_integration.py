import unittest
import hashlib,json
import numpy as np
import analyze as a

class IntegrationTests(unittest.TestCase):
    def test_original_engine_bytes(self):
        manifest=json.loads((a.HERE/'vendor/PROVENANCE.json').read_text())
        for path,digest in manifest['sha256'].items():
            self.assertEqual(hashlib.sha256((a.HERE/'vendor'/path).read_bytes()).hexdigest(),digest)
    def test_no_relations_leaves_neutral_parent(self):
        p=np.array([[.01,.99]]*3)
        for engine in ('hrl','grrle'):
            self.assertAlmostEqual(a.infer(p,engine,0)[0],.5)
            self.assertGreater(a.infer(p,engine,1)[0],.5)
            self.assertLess(a.infer(p,engine,1,True)[0],.5)
    def test_bayesian_likelihood_combination(self):
        rates=np.array([[2.,2.,8.],[12.,12.,2.]])
        x=np.array([[3,4,5]])
        p,llr=a.unary(x,rates)
        self.assertEqual(p.shape,(1,3,2))
        self.assertAlmostEqual(float(llr.sum()),7*np.log(6)-20+5*np.log(.25)+6)
    def test_splits_are_independent_scenes(self):
        train,y=a.sample(1101);valid,yv=a.sample(2202)
        self.assertFalse(np.array_equal(train,valid))
        before=a.fitted_rates(train,y).copy()
        valid[:]=99999
        np.testing.assert_array_equal(before,a.fitted_rates(train,y))
    def test_fuzzy_does_not_require_exclusivity(self):
        x=np.array([[10.,10.,10.]])
        self.assertGreater(float((x/(x+5)).sum()),1)
        self.assertAlmostEqual(float(a.fuzzy(x)[0]),1/3)
    def test_physical_trace_policy_control(self):
        with (a.HERE/'sensory-inference.csv').open() as f:
            import csv
            rows=list(csv.DictReader(f))
        light=[r for r in rows if r['scenario']=='light']
        decline=[r for r in rows if r['scenario']=='decline']
        self.assertEqual(len(light),15)
        for l,d in zip(light,decline):
            for key in ('left_events','right_events','hrl_external_score','grrle_external_score'):
                self.assertEqual(l[key],d[key])
        self.assertTrue(all(r['interoception']=='missing' for r in rows))
if __name__=='__main__':unittest.main()
