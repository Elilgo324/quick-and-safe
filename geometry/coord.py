import math
from typing import Tuple

from shapely import Point

from geometry.entity import Entity


class Coord(Entity):
    def __init__(self, x: float, y: float) -> None:
        self._x = x
        self._y = y
        self._shapely_shape = None

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def xy(self) -> Tuple[float, float]:
        return self.x, self.y

    @property
    def to_shapely(self) -> Point:
        if self._shapely_shape is None:
            self._shapely_shape = Point(self.x, self.y)
        return self._shapely_shape

    def shifted(self, distance: float, angle: float) -> 'Coord':
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        return Coord(self.x + x, self.y + y)

    def is_left_side_of_line(self, line_point1: 'Coord', line_point2: 'Coord') -> bool:
        return (line_point2.x - line_point1.x) * (self.y - line_point1.y) \
               - (line_point2.y - line_point1.y) * (self.x - line_point1.x) > 0

    def contact_points_with_circle(self, center: 'Coord', radius: float) -> Tuple['Coord', 'Coord']:
        # angle of pc line
        pc_angle = math.atan2(center.y - self.y, center.x - self.x) + math.pi

        # angle of deviation from pc line
        alpha = math.asin(radius / self.distance_to(center))

        left_contact_angle = pc_angle - alpha + 0.5 * math.pi
        right_contact_angle = pc_angle + alpha - 0.5 * math.pi

        left_contact_point = center.shifted(distance=radius, angle=left_contact_angle)
        right_contact_point = center.shifted(distance=radius, angle=right_contact_angle)

        # point should be on right of left-right line so flip if on left
        if self.is_left_side_of_line(left_contact_point, right_contact_point):
            return right_contact_point, left_contact_point

        return left_contact_point, right_contact_point

    def __eq__(self, other: 'Coord') -> bool:
        return self.x == other.x and self.y == other.y

    def almost_equal(self, other: 'Coord', epsilon: float = 1e-5) -> bool:
        return self.distance_to(other) < epsilon

    def __hash__(self):
        return hash(self.xy)

    def __str__(self):
        return f'Coord({self.x},{self.y})'
