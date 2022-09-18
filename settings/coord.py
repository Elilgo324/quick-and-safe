import math
from typing import Tuple

from shapely.geometry import Point


class Coord(Point):
    @property
    def xy(self) -> Tuple[float, float]:
        return self.x, self.y

    def shift(self, distance: float, angle: float) -> 'Coord':
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        return Coord(self.x + x, self.y + y)

    def is_left_side_of_line(self, line_point1: 'Coord', line_point2: 'Coord') -> bool:
        return (line_point2.x - line_point1.x) * (self.y - line_point1.y) \
               - (line_point2.y - line_point1.y) * (self.x - line_point1.x) > 0

    def contact_points_with_circle(self, center: 'Coord', radius: float) -> Tuple['Coord', 'Coord']:
        pc_angle = math.atan2(center.y - self.y, center.x - self.x)

        # fix according side of horizontal axis
        is_upside_down = self.y > center.y
        # if is_upside_down:
        pc_angle = math.pi + pc_angle

        alpha = math.asin(radius / self.distance(center))
        print(alpha)

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
