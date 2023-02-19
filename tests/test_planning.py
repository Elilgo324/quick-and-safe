import math

from algorithms.multiple_threats import multiple_threats_shortest_path
from algorithms.single_threat import single_threat_shortest_path, single_threat_safest_path, \
    single_threat_shortest_path_with_budget_constraint, _compute_s_t_contact_points
from algorithms.two_threats import two_threats_shortest_path_with_budget_constraint
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path


def test_shortest_path_single_threat():
    source = Coord(30, 80)
    target = Coord(30, 0)
    radius = 30
    circle = Circle(center=Coord(30, 40), radius=radius)

    path, length, risk = single_threat_shortest_path(source, target, circle)
    assert path == Path([source, target])
    assert length == source.distance_to(target)
    assert risk == 2 * radius


def test_safest_path_single_threat():
    center = Coord(30, 40)
    sources = [center.shifted(50, math.pi), center.shifted(60, 1)]
    targets = [center.shifted(50, 6), center.shifted(70, 3)]
    circle = Circle(center=center, radius=30)
    for source, target in zip(sources, targets):
        path, length, risk = single_threat_safest_path(source, target, circle)

        assert risk == 0
        assert length >= source.distance_to(target)
        assert length < source.distance_to(circle) \
               + target.distance_to(circle) \
               + 0.5 * Path.compute_path_length(circle.boundary)


def test_single_threat_shortest_path_with_risk_constraint():
    source = Coord(100, 100)
    target = Coord(-200, 90)
    circle = Circle(center=Coord(30, 40), radius=30)
    budget = 0
    path, length, risk \
        = single_threat_shortest_path_with_budget_constraint(source, target, circle, budget)

    assert path == Path([source, target])
    assert length == source.distance_to(target)
    assert risk == 0

    source = Coord(0, 40)
    target = Coord(100, 40)
    budget = 2 * circle.radius + 1
    path, length, risk \
        = single_threat_shortest_path_with_budget_constraint(source, target, circle, budget)

    assert length == source.distance_to(target)
    assert risk == 2 * circle.radius

    source = Coord(0, 100)
    target = Coord(100, 100)
    budget = 0
    path, length, risk \
        = single_threat_shortest_path_with_budget_constraint(source, target, circle, budget)
    s_path, s_length, s_risk = single_threat_safest_path(source, target, circle)

    assert path == s_path
    assert length == s_length
    assert risk == s_risk

    source = Coord(0, 50)
    target = Coord(100, 40)
    budget = 0
    path, length, risk \
        = single_threat_shortest_path_with_budget_constraint(source, target, circle, budget)
    s_path, s_length, s_risk = single_threat_safest_path(source, target, circle)

    assert path == s_path
    assert length == s_length
    assert risk == s_risk


def test_shortest_path():
    circles = [Circle(Coord(100, 100), 100), Circle(Coord(300, 500), 100), Circle(Coord(700, 700), 90)]
    source = Coord(0, 0)
    target = Coord(1000, 0)
    path, length, risk = multiple_threats_shortest_path(source, target, circles)
    assert path == Path([source, target])
    assert length == source.distance_to(target)
    assert risk == 0


def test_one_threat():
    circle = Circle(Coord(100, 100), 100)
    source = Coord(0, 0)
    target = Coord(200, 200)
    budget = circle.radius * 2
    path, length, risk = single_threat_shortest_path_with_budget_constraint(source, target, circle, budget)
    assert length == source.distance_to(target)
    assert risk == circle.radius * 2


def test_compute_s_t_contact_points():
    circle = Circle(Coord(100, 100), 100)
    source = Coord(0, 0)
    target = Coord(200, 200)

    s_contact, t_contact = _compute_s_t_contact_points(source, target, circle)
    assert s_contact.almost_equal(Coord(0, 100))
    assert t_contact.almost_equal(Coord(100, 200))


def test_single_threat_switch_s_t():
    circle = Circle(Coord(100, 100), 100)
    source = Coord(0, 0)
    target = Coord(200, 200)
    budget = 25
    p1, l1, r1 = single_threat_shortest_path_with_budget_constraint(source, target, circle, budget)
    p2, l2, r2 = single_threat_shortest_path_with_budget_constraint(target, source, circle, budget)
    assert abs(l1 - l2) < 1e-3 and abs(r1 - r2) < 1e-3

    budget = 75
    p1, l1, r1 = single_threat_shortest_path_with_budget_constraint(source, target, circle, budget)
    p2, l2, r2 = single_threat_shortest_path_with_budget_constraint(target, source, circle, budget)
    assert abs(l1 - l2) < 1e-3 and abs(r1 - r2) < 1e-3


def test_two_threats_switch_s_t_and_circles():
    circle1 = Circle(Coord(125, 100), 65)
    circle2 = Circle(Coord(275, 100), 65)
    source = Coord(0, 50)
    target = Coord(400, 125)
    budget = 100
    p1, l1, r1 = two_threats_shortest_path_with_budget_constraint(source, target, circle1, circle2, budget)
    p2, l2, r2 = two_threats_shortest_path_with_budget_constraint(target, source, circle1, circle2, budget)
    assert abs(l1 - l2) < 1e-3 and abs(r1 - r2) < 1e-3

    source = Coord(50, 140)
    target = Coord(350, 40)
    budget = 150
    p1, l1, r1 = two_threats_shortest_path_with_budget_constraint(source, target, circle1, circle2, budget)
    p2, l2, r2 = two_threats_shortest_path_with_budget_constraint(target, source, circle1, circle2, budget)
    assert abs(l1 - l2) < 1e-1 and abs(r1 - r2) < 1e-1

    source = Coord(50, 80)
    target = Coord(400, 80)
    budget = 150
    p1, l1, r1 = two_threats_shortest_path_with_budget_constraint(source, target, circle1, circle2, budget)
    p2, l2, r2 = two_threats_shortest_path_with_budget_constraint(source, target, circle2, circle1, budget)
    assert abs(l1 - l2) < 1e-3 and abs(r1 - r2) < 1e-3
