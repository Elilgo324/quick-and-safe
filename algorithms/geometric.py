import math
from typing import Tuple, List
from shapely.geometry.point import Point
from math import sqrt, acos, atan2, sin, cos

from settings.coord import Coord


def boundary_between_points(boundary: List[Coord], p1: Coord, p2: Coord) -> List[Coord]:
    start_idx = min(range(len(boundary)), key=lambda p: boundary[p].distance(p1))
    end_idx = min(range(len(boundary)), key=lambda p: boundary[p].distance(p2))
    return boundary[start_idx:end_idx + 1]


def is_left_side_of_line(line_point1: Coord, line_point2: Coord, point: Coord) -> bool:
    return (line_point2.x - line_point1.x) * (point.y - line_point1.y) \
           - (line_point2.y - line_point1.y) * (point.x - line_point1.x) > 0


def calculate_angle_on_chord(chord: float, radius: float) -> float:
    return 2 * math.asin(0.5 * chord / radius)


def calculate_angle_of_line(line_point1: Coord, line_point2: Coord) -> float:
    return math.atan((line_point1.y - line_point2.y) / (line_point1.x - line_point2.x))


def tangent_slopes_given_circle_and_point(center: Coord, radius: float, point: Coord) -> Tuple[float, float]:
    a = (center.x - point.x) ** 2 - radius ** 2
    b = 2 * (center.x - point.x) * (point.y - center.y)
    c = (point.y - center.y) ** 2 - radius ** 2

    m1 = (-b + sqrt(b ** 2 - 4 * a * c)) / 2 * a
    m2 = (-b - sqrt(b ** 2 - 4 * a * c)) / 2 * a

    return m1, m2


def contact_points_given_circle_and_point(center: Coord, radius: float, point: Coord) -> Tuple[Coord, Coord]:
    pc_angle = math.atan((center.y - point.y) / (center.x - point.x))

    # TBD CHECK what are the conditions
    # fix according side of horizontal axis
    # if center.y > point.y:
    #     pc_angle = pc_angle + math.pi

    alpha = math.asin(radius / center.distance(point))

    contact_angle1 = pc_angle - alpha + 0.5 * math.pi
    contact_angle2 = pc_angle + alpha - 0.5 * math.pi

    return center.shift(distance=radius, angle=contact_angle1), \
           center.shift(distance=radius, angle=contact_angle2)
