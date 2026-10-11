"""A didactic observation map; not a physical model or evidence about dark matter."""
from collections import defaultdict

states = [(mass, hidden_label) for mass in (1, 2) for hidden_label in ('a', 'b')]

def equivalence_classes(observations):
    classes = defaultdict(list)
    for state in states:
        record = tuple(observe(state) for observe in observations)
        classes[record].append(state)
    return list(classes.values())

if __name__ == '__main__':
    print('Restricted access (mass alone):', equivalence_classes([lambda x: x[0]]))
    print('Expanded access (mass and label):', equivalence_classes([lambda x: x[0], lambda x: x[1]]))
    print('Hiddenness was stipulated, not discovered. Expanded access removes it.')
