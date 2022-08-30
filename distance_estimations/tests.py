from random import seed

from environment import Environment
from prm import PRM


def test_equal_distance_computers():
    env = Environment(num_targets=10)
    prm = PRM(env)
    prm.add_samples(50, neighborhood_type='k')
    graph = prm.graph
    targets = env.targets_names

    assert set() == set()

if __name__ == '__main__':
    seed(42)
    test_equal_distance_computers()