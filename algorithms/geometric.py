import math
from typing import Tuple, List
from shapely.geometry.point import Point
from math import sqrt, acos, atan2, sin, cos
import matplotlib.pyplot as plt
from settings.coord import Coord


def is_left_side_of_line(line_point1: Coord, line_point2: Coord, point: Coord) -> bool:
    """Check if the turn: line point1 -> line point2 -> point is left turn

    :param line_point1: first line point
    :param line_point2: second line point
    :param point: the point
    :return: if the turn: line point1 -> line point2 -> point is left turn
    """
    return point.is_left_side_of_line(line_point1, line_point2)


def calculate_contact_points_with_circle_from_point(center: Coord, radius: float, point: Coord) -> Tuple[Coord, Coord]:
    """Calculates the two lines' contact points with the circle starting at a given outer point

    :param center: the center of the circle
    :param radius: the radius of the circle
    :param point: the outer point
    :return: the contact points
    """
    return point.contact_points_with_circle(center, radius)


def calculate_angle_on_chord(chord: float, radius: float) -> float:
    """Calculate the central angle that is supported by a given chord

    :param chord: the chord
    :param radius: the radius of the circle
    :return: the central angle that is supported by a given chord
    """
    return 2 * math.asin(0.5 * chord / radius)


def calculate_non_directional_angle_of_line(line_point1: Coord, line_point2: Coord) -> float:
    """Calculate the non-directional angle of a line

    :param line_point1: first line point
    :param line_point2: second line point
    :return: the non-directional angle of the line
    """
    # if vertical line
    if line_point1.x == line_point2.x:
        return 0.5 * math.pi

    return math.atan((line_point1.y - line_point2.y) / (line_point1.x - line_point2.x))


def calculate_directional_angle_of_line(start: Coord, end: Coord) -> float:
    """Calculate the directional angle of a line relative to the horizon

    :param start: the start of the line
    :param end: the end of the line
    :return: the directional angle of the line
    """
    # atan2 returns the angle between the positive x-axis and (x,y)
    angle = atan2(end.y - start.y, end.x - start.x)

    # if the angle is between -180 t0 0, add 360
    if angle < 0:
        angle += 2 * math.pi

    return angle


def calculate_points_in_distance_on_circle(center: Coord, radius: float, point: Coord, chord: float) \
        -> Tuple[Coord, Coord]:
    """Given a circle, a point and a chord distance, calculate the two points on the circle in this specific length

    :param center: the center of the circle
    :param radius: the radius of the circle
    :param point: the point
    :param chord: the chord
    :return: the two points on the circle in this specific length
    """
    angle_on_chord = calculate_angle_on_chord(chord, radius)
    angle_of_point = calculate_directional_angle_of_line(start=center, end=point)
    point1 = center.shift(distance=radius, angle=angle_of_point + angle_on_chord)
    point2 = center.shift(distance=radius, angle=angle_of_point - angle_on_chord)
    return point1, point2
