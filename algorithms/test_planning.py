import math

from algorithms.planning import shortest_path_single_threat, safest_path_single_threat, compute_path_length, \
    single_threat_shortest_path_with_risk_constraint
from settings.coord import Coord
from settings.threat import Threat
import matplotlib.pyplot as plt

source1 = Coord(8, 3)
target1 = Coord(-0.5, 4)

source2 = Coord(-5, -5)
target2 = Coord(25, 10)

sources = [source1, source2]
targets = [target1, target2]

threat = Threat(center=Coord(3, 4), radius=3)


def test_shortest_path_single_threat():
    path, length, risk = shortest_path_single_threat(source1, target1, threat)
    assert path == [source1, target1]
    assert length == source1.distance(target1)
    assert risk == 5.940567962907766


def test_safest_path_single_threat():
    for source, target in zip(sources, targets):
        path, length, risk = safest_path_single_threat(source, target, threat)

        assert risk == 0
        assert length > source.distance(target)
        assert length < source.distance(threat.polygon) \
               + target.distance(threat.polygon) \
               + 0.5 * compute_path_length(threat.boundary)

def test_single_threat_shortest_path_with_risk_constraint():
    source = Coord(100,100)
    target = Coord(-200,90)
    budget = 5
    path, length, risk \
        = single_threat_shortest_path_with_risk_constraint(source, target, threat, budget)

    assert length == source.distance(target)
    assert risk == 0

    source = Coord(-1,4)
    target = Coord(10,4)
    budget = 2 * threat.radius + 1
    path, length, risk \
        = single_threat_shortest_path_with_risk_constraint(source, target, threat, budget)

    assert length == source.distance(target)
    assert risk == 2 * threat.radius

    source = Coord(5, 10)
    target = Coord(0, -1)
    budget = 0
    path, length, risk \
        = single_threat_shortest_path_with_risk_constraint(source, target, threat, budget)
    s_path, s_length, s_risk = safest_path_single_threat(source, target, threat)

    plt.plot([p.x for p in s_path], [p.y for p in s_path], zorder=15)
    plt.plot([p.x for p in threat.boundary], [p.y for p in threat.boundary])
    plt.show()


    assert path == s_path
    assert length == s_length
    assert risk == s_risk


if __name__ == '__main__':
    test_shortest_path_single_threat()
    test_safest_path_single_threat()
    test_single_threat_shortest_path_with_risk_constraint()
