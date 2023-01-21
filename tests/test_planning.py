from shapely.geometry import LineString
from shapely.ops import nearest_points

from geometry.geometric import compute_path_length
from algorithms.single_threat import single_threat_shortest_path, single_threat_safest_path, \
    single_threat_shortest_path_with_budget_constraint
from geometry.coord import Coord
from geometry.circle import Circle

source1 = Coord(8, 3)
target1 = Coord(-0.5, 4)

source2 = Coord(-5, -5)
target2 = Coord(25, 10)

sources = [source1, source2]
targets = [target1, target2]

threat = Circle(center=Coord(3, 4), radius=3)


def test_shortest_path_single_threat():
    path, length, risk = single_threat_shortest_path(source1, target1, threat)
    assert path == [source1, target1]
    assert length == source1.distance_to(target1)
    assert abs(risk - 5.94) < 0.1


def test_safest_path_single_threat():
    for source, target in zip(sources, targets):
        path, length, risk = single_threat_safest_path(source, target, threat)

        assert risk == 0
        assert length > source.distance_to(target)
        assert length < source.distance_to(threat) \
               + target.distance_to(threat) \
               + 0.5 * compute_path_length(threat.boundary)


def test_single_threat_shortest_path_with_risk_constraint():
    source = Coord(100, 100)
    target = Coord(-200, 90)
    budget = 5
    path, length, risk, _ \
        = single_threat_shortest_path_with_budget_constraint(source, target, threat, budget)

    assert path == [source, target]
    assert length == source.distance_to(target)
    assert risk == 0

    source = Coord(-1, 4)
    target = Coord(10, 4)
    budget = 2 * threat.radius + 1
    path, length, risk, _ \
        = single_threat_shortest_path_with_budget_constraint(source, target, threat, budget)

    assert length == source.distance_to(target)

    assert risk == 2 * threat.radius

    source = Coord(5, 10)
    target = Coord(0, -1)
    budget = 0
    path, length, risk, _ \
        = single_threat_shortest_path_with_budget_constraint(source, target, threat, budget)
    s_path, s_length, s_risk = single_threat_safest_path(source, target, threat)

    # assert path == s_path
    assert abs(length - s_length) < 1e-3
    assert risk == s_risk

    source = Coord(3, 10)
    target = Coord(3, -5)
    budget = 2 * threat.radius - 1
    path, length, risk, _ \
        = single_threat_shortest_path_with_budget_constraint(source, target, threat, budget)

    one_after_source = path[1]
    one_before_target = path[-2]
    st_segment = LineString([source.to_shapely, target.to_shapely])

    assert risk == budget
    assert one_after_source.distance_to(nearest_points(st_segment, one_after_source.to_shapely)[0]) \
           < one_before_target.distance_to(nearest_points(st_segment, one_before_target.to_shapely)[0])

    target = Coord(3, -1)
    path, length, risk, _ \
        = single_threat_shortest_path_with_budget_constraint(source, target, threat, budget)

    one_after_source = path[1]
    one_before_target = path[-2]
    st_segment = LineString([source.to_shapely, target.to_shapely])

    assert one_after_source.distance_to(nearest_points(st_segment, one_after_source.to_shapely)[0]) \
           > one_before_target.distance_to(nearest_points(st_segment, one_before_target.to_shapely)[0])


def test_symetric_threats_symetric_lengths():
    pass


if __name__ == '__main__':
    test_shortest_path_single_threat()
    test_safest_path_single_threat()
    test_single_threat_shortest_path_with_risk_constraint()
    test_symetric_threats_symetric_lengths()
