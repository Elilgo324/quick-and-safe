import math

from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from geometry.segment import Segment


def test_coords_equality():
    assert Coord(40, -80) != Coord(40.0, -79.99999999999997)
    assert Coord(-200, 400) != Coord(-199.99999999999997, 400.0)
    assert Coord(40, -80).almost_equal(Coord(40.0, -79.99999999999997))
    assert Coord(-200, 400).almost_equal(Coord(-199.99999999999997, 400.0))


def test_circle_path_intersection():
    circle1 = Circle(center=Coord(100, 100), radius=100)
    circle2 = Circle(center=Coord(500, 100), radius=100)
    path = Path([Coord(-200, -400), Coord(-200, 100), Coord(550, 100)])
    assert circle1.path_intersection_length(path) + circle2.path_intersection_length(path) == 350


def test_vertical_segment():
    segment = Segment(Coord(0, -5), Coord(0, 5))
    assert Segment(Coord(-5, 0), Coord(5, 0)).almost_equal(segment.vertical_segment)
    segment = Segment(Coord(-3, -3), Coord(3, 3))
    assert Segment(Coord(-3, 3), Coord(3, -3)).almost_equal(segment.vertical_segment)


def test_circle_arc_length():
    circle = Circle(center=Coord(100, 100), radius=100)
    start = Coord(0, 100)
    end = Coord(200, 100)
    assert circle.arc_length_between(start, end) == circle.radius * math.pi

    end = Coord(100, 0)
    assert circle.arc_length_between(start, end) == circle.radius * math.pi * 0.5


def test_circle_boundary_between():
    circle = Circle(center=Coord(100, 100), radius=100)
    start = Coord(0, 100)
    end = Coord(200, 100)
    boundary_between = circle.get_boundary_between(start, end)
    assert circle.path_intersection_length(Path(boundary_between)) == 0
    assert boundary_between[0].almost_equal(start, 1) and boundary_between[-1].almost_equal(end, 1)
    assert 0 < math.pi * (circle.radius + circle.EPSILON) - Path(boundary_between).length < 1

    circle = Circle(center=Coord(100, 100), radius=200)
    start = Coord(100, 300)
    end = Coord(-100, 100)
    boundary_between = circle.get_boundary_between(start, end)
    assert circle.path_intersection_length(Path(boundary_between)) == 0
    assert boundary_between[0].almost_equal(start, 1) and boundary_between[-1].almost_equal(end, 1)
    assert 0 < 0.5 * math.pi * (circle.radius + circle.EPSILON) - Path(boundary_between).length < 1

    circle = Circle(center=Coord(500, 500), radius=500)
    start = Coord(0, 500)
    end = Coord(1000, 500)
    boundary_between = circle.get_boundary_between(start, end)
    assert circle.path_intersection_length(Path(boundary_between)) == 0
    assert boundary_between[0].almost_equal(start, 1) and boundary_between[-1].almost_equal(end, 1)
    assert 0 < math.pi * (circle.radius + circle.EPSILON) - Path(boundary_between).length < 1


def test_path_addition():
    path1 = Path([Coord(1, 1), Coord(2, 2)])
    path2 = Path([Coord(3, 3), Coord(4, 4)])
    merged_path = Path.concat_paths(path1, path2)
    assert merged_path.length == path1.length + path2.length + Path([path1.coords[-1], path2.coords[0]]).length
    assert merged_path.coords == path1.coords + path2.coords


def test_exit_point():
    r = 100
    center = Coord(200, 100)
    circle = Circle(center, r)
    start_point = center.shifted(r, 1)
    assert circle.calculate_exit_point(start_point, 2 * r, start_point) \
           == start_point.shifted(2 * r, Segment(start_point, center).angle)

    assert circle.calculate_exit_point(start_point, 1.5 * r, Coord(1000, 1000)).distance_to(start_point) == 1.5 * r
    assert circle.calculate_exit_point(start_point, 1 * r, Coord(1000, 1000)) \
           != circle.calculate_exit_point(start_point, 1 * r, Coord(-1000, -1000))
    assert abs(circle.calculate_exit_point(start_point, 1 * r, Coord(1000, 1000)).distance_to(start_point)
               - circle.calculate_exit_point(start_point, 1 * r, Coord(-1000, -1000)).distance_to(start_point)) < 1e-3

    circle = Circle(Coord(100, 100), 100)
    start_point = Coord(0, 100)
    chord = math.sqrt(100 ** 2 + 100 ** 2)
    assert circle.calculate_exit_point(start_point, chord, Coord(1000, 1000)).almost_equal(Coord(100, 200))
    assert circle.calculate_exit_point(start_point, chord, Coord(-1000, -1000)).almost_equal(Coord(100, 0))

    circle = Circle(Coord(200, 200), 200)
    start_point = Coord(200, 400)
    chord = math.sqrt(200 ** 2 + 200 ** 2)
    assert circle.calculate_exit_point(start_point, chord, Coord(1000, 1000)).almost_equal(Coord(400, 200))
    assert circle.calculate_exit_point(start_point, chord, Coord(-1000, -1000)).almost_equal(Coord(0, 200))


def test_partition_between_circles():
    r = 100
    source = Coord(0, 100)
    target = Coord(700, 100)
    center1 = Coord(200, 100)
    circle1 = Circle(center1, r)
    center2 = Coord(500, 100)
    circle2 = Circle(center2, r)
    partition = Circle.calculate_partition_between_circles(circle1, circle2, source, target, [circle1, circle2])
    assert partition.length == 2 * r

    source = Coord(0, 1000)
    partition = Circle.calculate_partition_between_circles(circle1, circle2, source, target, [circle1, circle2])
    assert 500 < partition.length < 1000

    center3 = Coord(1000, 1000)
    circle3 = Circle(center3, r)
    partition = Circle.calculate_partition_between_circles(circle1, circle2, source, target,
                                                           [circle1, circle2, circle3])
    assert 1000 < partition.length < 1100


def test_linsplit():
    segment = Segment(Coord(0, 0), Coord(100, 100))

    for p1, p2 in zip(segment.linsplit(3), [segment.start, segment.midpoint, segment.end]):
        assert p1.almost_equal(p2, 1e-5)


def test_linsplit_by_length():
    segments = [Segment(Coord(0, 0), Coord(100, 50)), Segment(Coord(-200, -10), Coord(100, 50))]

    for segment in segments:
        distance = 0.5
        amount = int(segment.length / distance)

        assert segment.linsplit(amount) == segment.linsplit_by_distance(distance)


def test_projection():
    c = Coord(10, 0)
    s = Segment(Coord(0, 0), Coord(10, 10))
    assert s.point_projection(c) == Coord(5, 5)

    c = Coord(0, 10)
    assert s.point_projection(c) == Coord(5, 5)
    assert Segment(s.end, s.start).point_projection(c) == Coord(5, 5)


def test_containment_of_sample_on_segment():
    segment = Segment(Coord(-15, -3), Coord(40, 37))
    samples = [segment.sample() for _ in range(10)]
    assert all([segment.contains(sample) for sample in samples])
