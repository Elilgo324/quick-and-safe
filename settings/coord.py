import math
from typing import Tuple

from shapely.geometry import Point


class Coord(Point):
    @property
    def xy(self) -> Tuple[float, float]:
        """Gets the x,y of the coordinate

        :return: the x,y of the coordinate
        """
        return self.x, self.y

    def shift(self, distance: float, angle: float) -> 'Coord':
        """Shifts the coord by a given distance and angle

        :param distance: the distance
        :param angle: the angle
        :return: the shifted coord by a given distance and angle
        """
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        return Coord(self.x + x, self.y + y)

    def is_left_side_of_line(self, line_point1: 'Coord', line_point2: 'Coord') -> bool:
        """Checks if a given segment and this coord makes a left turn

        :param line_point1: the first point of the segment
        :param line_point2: the second point of the segment
        :return: if a given segment and this coord makes a left turn
        """
        return (line_point2.x - line_point1.x) * (self.y - line_point1.y) \
               - (line_point2.y - line_point1.y) * (self.x - line_point1.x) > 0

    def contact_points_with_circle(self, center: 'Coord', radius: float) -> Tuple['Coord', 'Coord']:
        """Computes the two contact points of this coord and a circle

        :param center: the center of the circle
        :param radius: the radius of the circle
        :return: the contact points of this coord and the circle
        """
        # angle of pc line
        pc_angle = math.atan2(center.y - self.y, center.x - self.x) + math.pi

        # angle of deviation from pc line
        alpha = math.asin(radius / self.distance(center))

        left_contact_angle = pc_angle - alpha + 0.5 * math.pi
        right_contact_angle = pc_angle + alpha - 0.5 * math.pi

        left_contact_point = center.shift(distance=radius, angle=left_contact_angle)
        right_contact_point = center.shift(distance=radius, angle=right_contact_angle)

        # point should be on right of left-right line so flip if on left
        if self.is_left_side_of_line(left_contact_point, right_contact_point):
            return right_contact_point, left_contact_point

        return left_contact_point, right_contact_point

    def __hash__(self):
        return hash(self.xy)

    def __str__(self):
        return f'Coord({self.x},{self.y})'

    def almost_equal(self, other: 'Coord', epsilon: float = 1e-5) -> bool:
        """Checks if other coord is almost equal to this coord up to some epsilon

        :param other: other coord
        :param epsilon: epsilon for equality check
        :return: if other coord is almost equal to this coord
        """
        return abs(self.x - other.x) < epsilon and abs(self.y - other.y) < epsilon
