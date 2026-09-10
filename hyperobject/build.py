"""Generate the inspectable musical hyperobject; Python standard library only."""
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
vertices = list(itertools.product([0, 1], repeat=3))
edges = [(a, b) for a in range(8) for b in range(a+1, 8)
         if sum(x != y for x, y in zip(vertices[a], vertices[b])) == 1]
u = [[1/math.sqrt(12) if n == 0 else math.sqrt(2/12)*math.cos(math.pi*(j+.5)*n/12)
      for n in range(12)] for j in range(12)]
frequencies = [440*2**((n-9)/12) for n in range(12)]
obj = {
    'name': 'C — Musical Hyperobject', 'version': 1,
    'interpretive_descriptors': {'error_corrector': 'God',
                                 'meaning': 'User-provided theological interpretation; not an implemented mechanism or mathematical result.'},
    'status': 'Constructed mathematical and musical model; not a physical string-theory derivation.',
    'carrier': {'symbol': 'C', 'spatial_dimension': 0,
                'meaning': 'A named point carrying internal state; not the empty set.',
                'undecidable': 'Unformalized descriptor: no proposition and formal system specified.'},
    'notes': [{'index': n, 'pitch_class': name, 'register': name+'4', 'frequency_hz': frequencies[n]}
              for n, name in enumerate(names)],
    'state': {'active_pitch_classes': [0, 4, 7], 'weights': [1/3 if n in [0,4,7] else 0 for n in range(12)],
              'gain': .15, 'phases_radians': [0]*12, 'palette': 'white',
              'rules': 'Nonempty weights sum to one. Empty selection is silence with all weights zero, outside the normalized simplex.'},
    'geometry': {'simplex_dimension': 11, 'vertices': 12,
                 'cube_vertices': vertices, 'cube_edges': [{'vertices': e, 'mode_index': n} for n,e in enumerate(edges)],
                 'cube_meaning': 'Eight binary color choices and twelve edges; an organizational view, not the simplex embedding.'},
    'palettes': {'black': ['cyan','magenta','yellow'], 'white': ['red','green','blue'],
                 'meaning': 'User-defined palette names; visual state only, does not change dynamics.'},
    'three_in_one': {'meaning': 'A triad is one chord identity expressed by three pitch classes.',
                     'qualities_semitones': {'major':[0,4,7], 'minor':[0,3,7], 'diminished':[0,3,6], 'augmented':[0,4,8]}},
    'progression': [{'name':name,'notes':notes} for name,notes in [
        ('C',[0,4,7]),('Dm',[2,5,9]),('Em',[4,7,11]),('F',[5,9,0]),
        ('G',[7,11,2]),('Am',[9,0,4]),('Bdim',[11,2,5]),('C',[0,4,7])]],
    'seal': {'chord':'Bdim','meaning':'User-defined name for the seventh diatonic triad.'},
    'collections': {'counts_by_size': [math.comb(12,k) for k in range(13)],
                    'total_including_empty':4096, 'trichords':[list(c) for c in itertools.combinations(range(12),3)],
                    'equivalence':'Order and octave ignored; transposed pitch-class sets remain distinct.'},
    'dynamics': {'signal':'gain * sum(weight[n] * sin(2*pi*frequency[n]*time + phase[n]))',
                 'equation':'x_double_dot + K*x = 0; x = U*q', 'mode_basis_U':u,
                 'coupling_K': [[sum(u[i][n]*(2*math.pi*frequencies[n])**2*u[j][n] for n in range(12)) for j in range(12)] for i in range(12)],
                 'meaning':'General internal coupling chosen to realize the musical spectrum; not nearest-neighbor cube coupling.'}
}
(ROOT/'hyperobject.json').write_text(json.dumps(obj, indent=2)+'\n')
template = (ROOT/'template.html').read_text()
(ROOT/'index.html').write_text(template.replace('__OBJECT_JSON__', json.dumps(obj)))
print('Built hyperobject.json and standalone index.html')
