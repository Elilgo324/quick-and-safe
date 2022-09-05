import math
from typing import Tuple
from shapely.geometry.point import Point
from math import sqrt, acos, atan2, sin, cos


def is_left_side_of_line(line_point1: Point, line_point2: Point, point: Point) -> bool:
    """Checks if point is on the left of the line using a cross product

    :param line_point1: the first line point
    :param line_point2: the second line point
    :param point: point to check if on left
    :return: if point is on the left
    """
    return (line_point2.x - line_point1.x) * (point.y - line_point1.y) \
           - (line_point2.y - line_point1.y) * (point.x - line_point1.x) > 0


def shift_point(point: Point, distance: float, angle: float) -> Point:
    """Shift point by distance in angle direction

    :param point: the point
    :param distance: distance to shift
    :param angle: the angle of the shift
    :return: the shifted point
    """
    x = distance * math.cos(angle)
    y = distance * math.sin(angle)
    return Point(point.x + x, point.y + y)


def calculate_angle_on_chord(chord: float, radius: float) -> float:
    """Calculate angle that is supported by chord

    :param chord: the chord
    :param radius: the radius of the circle
    :return: the angle that is supported by chord
    """
    return 2 * math.asin(0.5 * chord / radius)


def calculate_angle_of_line(line_point1: Point, line_point2: Point) -> float:
    """Calculate angle of a line relative to the horizon

    :param line_point1: first line point
    :param line_point2: second line point
    :return: angle of the line relative to the horizon
    """
    return math.atan((line_point1.y - line_point2.y) / (line_point1.x - line_point2.x))


def tangent_slopes_given_circle_and_point(center: Point, radius: float, point: Point) -> Tuple[float, float]:
    """Calculates tangent slopes of a given circle and an outer point

    :param center: the center of the circle
    :param radius: the radius of the circle
    :param point: the outer point
    :return: the tangent slopes of a given circle and an outer point
    """
    a = (center.x - point.x) ** 2 - radius ** 2
    b = 2 * (center.x - point.x) * (point.y - center.y)
    c = (point.y - center.y) ** 2 - radius ** 2

    m1 = (-b + sqrt(b ** 2 - 4 * a * c)) / 2 * a
    m2 = (-b - sqrt(b ** 2 - 4 * a * c)) / 2 * a

    return m1, m2


def contact_points_given_circle_and_point(center: Point, radius: float, point: Point) -> Tuple[Point, Point]:
    """Calculate cantact points of a given circle and outer point

    :param center: the center of the circle
    :param radius: the radius of the circle
    :param point: the outer point
    :return: the cantact points of a given circle and outer point
    """
    (Px, Py) = (point.x, point.y)
    (Cx, Cy) = (center.x, center.y)
    a = radius

    b = sqrt((Px - Cx) ** 2 + (Py - Cy) ** 2)  # hypot() also works here
    th = acos(a / b)  # angle theta
    d = atan2(Py - Cy, Px - Cx)  # direction angle of point P from C
    d1 = d + th  # direction angle of point T1 from C
    d2 = d - th  # direction angle of point T2 from C

    T1x = Cx + a * cos(d1)
    T1y = Cy + a * sin(d1)
    T2x = Cx + a * cos(d2)
    T2y = Cy + a * sin(d2)

    return Point(T1x, T1y), Point(T2x, T2y)