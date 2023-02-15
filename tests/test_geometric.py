import math

from geometry.coord import Coord
from geometry.geometric import is_left_side_of_line, calculate_angle_on_chord, \
    calculate_non_directional_angle_of_line, calculate_directional_angle_of_line, \
    calculate_points_in_distance_on_circle, calculate_contact_points_with_circle_from_point, \
    calculate_arc_length_on_chord, calculate_outer_tangent_points_of_circles, calculate_inner_tangent_points_of_circles


def test_is_left_side_of_line():
    l1 = Coord(-5, -5)
    l2 = Coord(5, -5)
    p = Coord(0, 0)
    assert is_left_side_of_line(l1, l2, p)

    l1 = Coord(1, 4)
    l2 = Coord(-10, -20)
    p = Coord(-30, 30)
    assert not is_left_side_of_line(l1, l2, p)


def test_calculate_contact_points_with_circle_from_point():
    center = Coord(2, 2)
    radius = 2
    point = Coord(4, 4)
    assert set(calculate_contact_points_with_circle_from_point(center, radius, point)) == {Coord(2, 4), Coord(4, 2)}

    point = Coord(4, 0)
    assert set(calculate_contact_points_with_circle_from_point(center, radius, point)) \
           == {Coord(1.9999999999999996, 0.0), Coord(4.0, 1.9999999999999996)}

    point = Coord(0, 0)
    assert set(calculate_contact_points_with_circle_from_point(center, radius, point)) \
           == {Coord(0.0, 2.0000000000000004), Coord(1.9999999999999996, 0.0)}


def test_calculate_angle_on_chord():
    radius = 1
    chord = 2
    assert calculate_angle_on_chord(chord, radius) == math.pi

    radius = 8.7
    chord = math.sqrt(2) * radius
    assert abs(calculate_angle_on_chord(chord, radius) - 0.5 * math.pi) < 1e-8


def test_calculate_arc_length_on_chord():
    radius = 1
    chord = 2
    assert calculate_arc_length_on_chord(chord, radius) == math.pi * radius

    radius = 1
    chord = radius * math.sqrt(2)
    assert abs(calculate_arc_length_on_chord(chord, radius) - 0.5 * math.pi * radius) < abs(1e-8)


def test_calculate_non_directional_angle_of_line():
    p1 = Coord(0, 0)
    p2 = Coord(8, 8)
    assert calculate_non_directional_angle_of_line(p1, p2) == 0.25 * math.pi
    assert calculate_non_directional_angle_of_line(p2, p1) == 0.25 * math.pi

    p1 = Coord(10, -4)
    p2 = Coord(10, -14)
    assert calculate_non_directional_angle_of_line(p1, p2) == 0.5 * math.pi


def test_calculate_directional_angle_of_line():
    p1 = Coord(1, 1)
    p2 = Coord(9, 9)
    assert calculate_directional_angle_of_line(p1, p2) == 0.25 * math.pi
    assert calculate_directional_angle_of_line(p2, p1) == 1.25 * math.pi

    p1 = Coord(0, 0)
    p2 = Coord(1, -1)
    assert calculate_directional_angle_of_line(p1, p2) == 1.75 * math.pi
    assert calculate_directional_angle_of_line(p2, p1) == 0.75 * math.pi

    p1 = Coord(10, -4)
    p2 = Coord(10, -14)
    assert calculate_directional_angle_of_line(p1, p2) == 1.5 * math.pi
    assert calculate_directional_angle_of_line(p2, p1) == 0.5 * math.pi


def test_calculate_points_in_distance_on_circle():
    center = Coord(2, 2)
    radius = 2
    point = Coord(4, 2)
    chord = math.sqrt(2) * radius
    assert set(calculate_points_in_distance_on_circle(center, radius, point, chord)) \
           == {Coord(1.9999999999999998, 0.0), Coord(1.9999999999999998, 4.0)}

    center = Coord(-8, -9)
    radius = 5
    point = Coord(-3, -9)
    chord = 3.24
    p1, p2 = calculate_points_in_distance_on_circle(center, radius, point, chord)
    assert abs(p1.distance_to(point) - p2.distance_to(point)) < 1e-8
    assert abs(p1.distance_to(point) - chord) < 1e-8
    assert abs(p1.distance_to(center) - p2.distance_to(center)) < 1e-8
    assert abs(p1.distance_to(center) - radius) < 1e-8


def test_pairs_of_outer_tangent_points_on_circle():
    center1 = Coord(100, 100)
    center2 = Coord(500, 100)
    radius = 100
    assert set(calculate_outer_tangent_points_of_circles(center1, radius, center2, radius)) \
           == {Coord(100, 200), Coord(100, 0), Coord(500, 200), Coord(500, 0)}

    center1 = Coord(-200, 100)
    center2 = Coord(200, 300)
    radius1 = 300
    radius2 = 100
    result = calculate_outer_tangent_points_of_circles(center1, radius1, center2, radius2)
    gt = [Coord(-200, 400), Coord(40, -80), Coord(200, 400), Coord(280, 240)]
    assert all([c1.almost_equal(c2) for c1, c2 in zip(result, gt)])

    center1 = Coord(0, 150)
    center2 = Coord(0, 0)
    radius1 = 50
    radius2 = 90
    result = calculate_outer_tangent_points_of_circles(center1, radius1, center2, radius2)
    print(result)
    gt = [Coord(-48.18944098, 163.33333333), Coord(48.18944098, 163.3333333), Coord(-86.740993, 24),
          Coord(86.74099376, 24)]
    assert all([c1.almost_equal(c2) for c1, c2 in zip(result, gt)])

    center1 = Coord(100, 300)
    center2 = Coord(-100, 100)
    radius1 = 100
    radius2 = 300
    assert set(calculate_outer_tangent_points_of_circles(center1, radius1, center2, radius2)) \
           == set(calculate_outer_tangent_points_of_circles(center2, radius2, center1, radius1))


def test_pairs_of_inner_tangent_points_on_circle():
    center1 = Coord(100, 100)
    center2 = Coord(500, 100)

    radius = 100

    t1, t2, t3, t4 = calculate_inner_tangent_points_of_circles(center1, radius, center2, radius)

    assert t1.distance_to(t2) == t3.distance_to(t4)
    assert abs(t1.distance_to(t3) - t2.distance_to(t4)) < 1e-3
    assert t1.distance_to(center1) < t3.distance_to(center1)

    t1, t2, t3, t4 = calculate_inner_tangent_points_of_circles(center1, radius, center2, 2 * radius)

    assert t1.distance_to(t2) < t3.distance_to(t4)
    assert abs(t1.distance_to(t3) - t2.distance_to(t4)) < 1e-3
    assert t1.distance_to(center1) < t3.distance_to(center1)

    t1, t2, t3, t4 = calculate_inner_tangent_points_of_circles(center2, radius, center1, radius)

    assert t1.distance_to(t2) == t3.distance_to(t4)
    assert abs(t1.distance_to(t3) - t2.distance_to(t4)) < 1e-3
    assert t1.distance_to(center2) < t3.distance_to(center2)

    t1, t2, t3, t4 = calculate_inner_tangent_points_of_circles(center2, radius, center1, 2 * radius)

    assert t1.distance_to(t2) < t3.distance_to(t4)
    assert abs(t1.distance_to(t3) - t2.distance_to(t4)) < 1e-3
    assert t1.distance_to(center2) < t3.distance_to(center2)
