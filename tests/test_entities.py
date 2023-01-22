import math

from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from geometry.segment import Segment


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


if __name__ == '__main__':
    test_circle_path_intersection()
    test_vertical_segment()
    test_circle_boundary_between()
