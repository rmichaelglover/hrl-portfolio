import unittest
from replay import decode,evaluate

def row(c,n,s=10,q=.95):return dict(trial='t',party='ants',candidate=c,events=n,visible_seconds=s,confidence=q)
class ReplayTests(unittest.TestCase):
 def test_rates(self):self.assertEqual(decode([row('A',10,100),row('B',5)])[0]['choice'],'B')
 def test_abstention(self):
  for rows in ([row('A',1),row('B',1)],[row('A',0),row('B',0)],[row('A',8),row('B',1,q=.1)]):
   self.assertIsNone(decode(rows)[0]['choice'])
 def test_scores(self):
  r=evaluate(decode([row('A',8),row('B',1)]),{'t':{'A':2,'B':8}})
  self.assertEqual(r['means']['decoded_cost'],2);self.assertEqual(r['means']['random_expected_cost'],5)
  self.assertEqual(r['coverage'],1)
 def test_invalid(self):
  for bad in (row('A',-1),row('A',1,0),row('A',float('nan')),row('A',1,q=2)):
   with self.assertRaises(ValueError):decode([bad,row('B',1)])
  with self.assertRaises(ValueError):decode([row('A',1),row('A',2)])
  with self.assertRaises(ValueError):evaluate(decode([row('A',2),row('B',1)]),{'t':{'A':2}})
if __name__=='__main__':unittest.main()
