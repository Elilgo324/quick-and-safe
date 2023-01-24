import math
from math import atan2
from typing import Tuple

from geometry.coord import Coord


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
    return 2 * math.asin(min(0.5 * chord / radius, 1))


def calculate_arc_length_on_chord(chord: float, radius: float) -> float:
    """Calculate the arc length of a given chord length

    :param chord: the chord length
    :param radius: the radius of the circle
    :return: length on the arc supported by the chord
    """
    return calculate_angle_on_chord(chord, radius) * radius


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
    chord = min(chord, 2 * radius)
    angle_on_chord = calculate_angle_on_chord(chord, radius)
    angle_of_point = calculate_directional_angle_of_line(start=center, end=point)
    point1 = center.shifted(distance=radius, angle=angle_of_point + angle_on_chord)
    point2 = center.shifted(distance=radius, angle=angle_of_point - angle_on_chord)
    return point1, point2


def calculate_tangent_points_of_circles(center1: Coord, radius1: float, center2: Coord, radius2: float) \
        -> Tuple[Coord, Coord, Coord, Coord]:
    """Calculate the two pairs of tangent points of two circles

    :param center1: the center of circle1
    :param radius1: the radius of circle1
    :param center2: the center of circle2
    :param radius2: the radius of circle2
    :return: the two pairs of tangent points of two circles
    """
    centers_segment_length = center1.distance_to(center2)
    centers_segment_angle = calculate_directional_angle_of_line(center1, center2)

    theta1 = math.acos(centers_segment_length / abs(radius1 - radius2))
    theta2 = math.pi - theta1

    if radius2 > radius1:
        temp = theta1
        theta1 = theta2
        theta2 = temp

    upper_theta1 = centers_segment_angle + theta1
    upper_theta2 = centers_segment_angle + theta2

    lower_theta1 = centers_segment_angle - theta1
    lower_theta2 = centers_segment_angle - theta2

    return center1.shifted(radius1, upper_theta1), center2.shifted(radius2, upper_theta2), \
           center1.shifted(radius1, lower_theta1), center2.shifted(radius2, lower_theta2)
