import math

from geometry.geometric import is_left_side_of_line, calculate_angle_on_chord, \
    calculate_non_directional_angle_of_line, calculate_directional_angle_of_line, \
    calculate_points_in_distance_on_circle, calculate_contact_points_with_circle_from_point, \
    calculate_arc_length_on_chord
from geometry.coord import Coord
from geometry.segment import Segment


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


if __name__ == '__main__':
    test_is_left_side_of_line()
    test_calculate_contact_points_with_circle_from_point()
    test_calculate_angle_on_chord()
    test_calculate_arc_length_on_chord()
    test_calculate_non_directional_angle_of_line()
    test_calculate_directional_angle_of_line()
    test_calculate_points_in_distance_on_circle()
