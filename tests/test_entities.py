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
    assert circle1.compute_path_risk(path) + circle2.compute_path_risk(path) == 350


def test_vertical_segment():
    segment = Segment(Coord(0, -5), Coord(0, 5))
    assert Segment(Coord(-5, 0), Coord(5, 0)).almost_equal(segment.vertical_segment)
    segment = Segment(Coord(-3, -3), Coord(3, 3))
    assert Segment(Coord(-3, 3), Coord(3, -3)).almost_equal(segment.vertical_segment)


def test_circle_boundary_between():
    circle = Circle(center=Coord(100, 100), radius=100)
    start = Coord(0, 100)
    end = Coord(200, 100)
    boundary_between = circle.get_boundary_between(start, end)
    assert circle.compute_path_risk(Path(boundary_between)) == 0
    assert boundary_between[0].almost_equal(start, 1) and boundary_between[-1].almost_equal(end, 1)
    assert 0 < math.pi * (circle.radius + circle.EPSILON) - Path(boundary_between).length < 1

    circle = Circle(center=Coord(100, 100), radius=200)
    start = Coord(100, 300)
    end = Coord(-100, 100)
    boundary_between = circle.get_boundary_between(start, end)
    assert circle.compute_path_risk(Path(boundary_between)) == 0
    assert boundary_between[0].almost_equal(start, 1) and boundary_between[-1].almost_equal(end, 1)
    assert 0 < 0.5 * math.pi * (circle.radius + circle.EPSILON) - Path(boundary_between).length < 1

    circle = Circle(center=Coord(500, 500), radius=500)
    start = Coord(0, 500)
    end = Coord(1000, 500)
    boundary_between = circle.get_boundary_between(start, end)
    assert circle.compute_path_risk(Path(boundary_between)) == 0
    assert boundary_between[0].almost_equal(start, 1) and boundary_between[-1].almost_equal(end, 1)
    assert 0 < math.pi * (circle.radius + circle.EPSILON) - Path(boundary_between).length < 1


def test_path_addition():
    path1 = Path([Coord(1, 1), Coord(2, 2)])
    path2 = Path([Coord(3, 3), Coord(4, 4)])
    merged_path = Path.concat_paths(path1, path2)
    assert merged_path.length == path1.length + path2.length + Path([path1.coords[-1], path2.coords[0]]).length
    assert merged_path.coords == path1.coords + path2.coords
