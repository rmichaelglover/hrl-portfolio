import json
from pathlib import Path
import unittest
from cypher_robot_mind.peaceful import Garden, Person, separation, chess_profile

ROOT = Path(__file__).resolve().parents[1]
class PeacefulTests(unittest.TestCase):
    def profile(self):
        return json.loads((ROOT/'config/peaceful-profile.json').read_text())
    def test_crossing_and_swap_are_collisions(self):
        self.assertEqual(separation((0,0),(1,0),(1,0),(0,0)),0)
        self.assertEqual(separation((0,1),(2,1),(1,0),(1,2)),0)
    def test_entire_replay_protects_every_neighbor(self):
        world=Garden(self.profile())
        for tick in range(40):
            old=[p.position for p in world.people]
            world.step()
            for i,p in enumerate(world.people):
                self.assertTrue(world.valid(p.position))
                self.assertGreaterEqual(separation(old[i],p.position,world.frog(tick),world.frog(tick+1)),.65)
                for j in range(i):
                    self.assertGreaterEqual(separation(old[i],p.position,old[j],world.people[j].position),.75)
        self.assertTrue(all(p.position==p.goal for p in world.people))
        self.assertGreaterEqual(sum(p.rose_pauses for p in world.people),4)
        self.assertTrue(world.people[0].wants_prosthetic_support)
    def test_frog_swept_hop_excluded(self):
        world=Garden(self.profile())
        world.tick_count=2 # frog goes from (3,5) to (3,6)
        person=Person('Test',(3,6),(3,5))
        self.assertNotIn((3,5),world.candidates(person))
    def test_preference_change_changes_rose_pause(self):
        world=Garden(self.profile())
        person=world.people[0]
        person.position=(2,2)
        world.distance_cache={p.name:world.distances(p) for p in world.people}
        self.assertGreater(world.utility(person,(2,2)),world.utility(person,(3,2)))
        person.rose_interest=0
        self.assertLess(world.utility(person,(2,2)),world.utility(person,(3,2)))
    def test_recorded_geometry_changes_weights(self):
        a=chess_profile('1. e4 d5 2. exd5 Qxd5 *')
        b=chess_profile('1. e4 e5 2. Nf3 Nc6 *')
        self.assertEqual(a['plies'],4)
        self.assertLess(a['weights']['progress'],b['weights']['progress'])
        with self.assertRaises(ValueError): chess_profile('')
    def test_no_joint_action_commits_nothing(self):
        world=Garden(self.profile())
        world.candidates=lambda person: []
        old=[p.position for p in world.people]
        with self.assertRaises(RuntimeError): world.step()
        self.assertEqual(old,[p.position for p in world.people])
        self.assertEqual(world.tick_count,0)
if __name__=='__main__': unittest.main()
