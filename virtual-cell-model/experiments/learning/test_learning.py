import csv,json,subprocess,tempfile,unittest
from pathlib import Path
import numpy as np
import prepare
import train
ROOT=Path(__file__).resolve().parents[2]
BINARY=ROOT/'build/relaxation_learning'
class LearningChecks(unittest.TestCase):
    def test_cpp_gradient_matches_pytorch_autograd(self):
        import torch
        result=json.loads(subprocess.check_output([str(BINARY),'probe'],text=True))
        p=torch.tensor(result['parameters'],dtype=torch.float64,requires_grad=True)
        x=torch.tensor([[-.8,.3],[.5,.8],[.1,-.6],[.9,-.2]],dtype=torch.float64)
        adjacency=torch.tensor([[0,.7,.3,0],[1,0,0,0],[0,0,0,0],[0,0,0,1]],dtype=torch.float64)
        b=x@p[:4].reshape(2,2)+p[4:6];compatibility=p[6:].reshape(2,2)
        strengths=torch.softmax(b,dim=1)
        for _ in range(3):strengths=.5*strengths+.5*torch.softmax(b+adjacency@strengths@compatibility.T,dim=1)
        loss=-torch.log(strengths[[0,1,3],[0,1,1]]).mean();loss.backward()
        np.testing.assert_allclose(strengths.detach().numpy(),result['strengths'],rtol=1e-13,atol=1e-14)
        np.testing.assert_allclose(p.grad.numpy(),result['gradient'],rtol=1e-11,atol=1e-13)
        self.assertAlmostEqual(loss.item(),result['loss'],places=13)
    def test_shuffle_preserves_unary_feature_target_pairs(self):
        rows=[dict(recording='a',epoch=i*2,label=i%2,features=np.full(6,i/10)) for i in range(10)]
        with tempfile.TemporaryDirectory() as folder:
            files=[Path(folder)/'original.txt',Path(folder)/'shuffled.txt']
            for path,seed in zip(files,[None,442]):prepare.write_data(path,rows,np.zeros(6),np.ones(6),seed)
            parsed=[np.loadtxt(p,skiprows=1) for p in files]
            self.assertEqual(sorted(map(tuple,parsed[0][:,2:])),sorted(map(tuple,parsed[1][:,2:])))
            self.assertFalse(np.array_equal(parsed[0][:,1],parsed[1][:,1]))
    def test_transform_uses_supplied_training_rows_only(self):
        rows=[dict(features=np.array([1.,2.])),dict(features=np.array([3.,4.]))]
        mean,std=prepare.fit_transform(rows)
        np.testing.assert_array_equal(mean,[2,3]);np.testing.assert_array_equal(std,[1,1])
        self.assertTrue(all('stage' not in k and 'code' not in k for k in prepare.FEATURES))
    def test_readout_probabilities_and_gradient_are_finite(self):
        result=json.loads(subprocess.check_output([str(BINARY),'probe'],text=True))
        p=np.array(result['strengths']);self.assertTrue(np.all(np.isfinite(result['gradient'])))
        np.testing.assert_allclose(p.sum(axis=1),1,atol=1e-14)
    def test_heldout_metrics_handle_ties(self):
        result=train.measures(np.array([0,1,1,0]),np.array([.1,.2,.9,.9]))
        self.assertAlmostEqual(result['roc_auc'],.625)
        self.assertAlmostEqual(result['average_precision'],7/12)
        self.assertAlmostEqual(result['macro_f1'],.5)
        self.assertAlmostEqual(result['brier'],.3675)
        self.assertAlmostEqual(result['ece_10_bins'],.425)
    def test_cli_trains_saves_and_reloads(self):
        rows=[dict(recording='toy',epoch=i,label=int(i>=20),features=np.array([-1. if i<20 else 1.]*6)) for i in range(40)]
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);data=folder/'toy.txt';prepare.write_data(data,rows,np.zeros(6),np.ones(6))
            model=folder/'model.txt';history=folder/'history.csv'
            output=subprocess.check_output([str(BINARY),'train',str(data),str(data),str(model),str(history),'6','80','73','.02'],text=True)
            report=json.loads(output);self.assertLess(report['training_nll'],.1)
            predictions=subprocess.check_output([str(BINARY),'predict',str(model),str(data)],text=True)
            self.assertEqual(len(predictions.splitlines()),41)
            self.assertLessEqual(report['contraction_bound'],.875+1e-12)
if __name__=='__main__':unittest.main()
