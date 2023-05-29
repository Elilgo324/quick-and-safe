import math
import random
from typing import Tuple, List

import matplotlib.pyplot as plt
from shapely.geometry import LineString

from geometry.coord import Coord
from geometry.entity import Entity
from geometry.geometric import calculate_directional_angle_of_line


class Segment(Entity):
    def __init__(self, start: Coord, end: Coord) -> None:
        self._start = start
        self._end = end
        self._slope = None
        self._angle = None
        self._shapely_shape = None
        self._vertical_segment = None

    @property
    def start(self) -> Coord:
        return self._start

    @property
    def end(self) -> Coord:
        return self._end

    @property
    def endpoints(self) -> Tuple[Coord, Coord]:
        return (self._start, self._end)

    @property
    def perimeter(self) -> float:
        return self.length

    @property
    def length(self) -> float:
        return self._start.distance_to(self._end)

    @property
    def angle(self) -> float:
        if self._angle is None:
            self._angle = calculate_directional_angle_of_line(self.start, self.end)
        return self._angle

    @property
    def slope(self) -> float:
        if self._slope is None:
            self._slope = (self.start.y - self.end.y) / (self.start.x - self.end.x)
        return self._slope

    @property
    def vertical_segment(self) -> 'Segment':
        if self._vertical_segment is None:
            self._vertical_segment = Segment(
                self.midpoint.shifted(self.length / 2, self.angle + math.pi / 2),
                self.midpoint.shifted(self.length / 2, self.angle - math.pi / 2)
            )
        return self._vertical_segment

    def extended(self, distance) -> 'Segment':
        extended_start = self.start.shifted(distance, self.angle + math.pi)
        extended_end = self.end.shifted(distance, self.angle)
        return Segment(extended_start, extended_end)

    @property
    def midpoint(self) -> Coord:
        return Coord((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2)

    @property
    def to_shapely(self) -> LineString:
        if self._shapely_shape is None:
            self._shapely_shape = LineString([self.start.to_shapely, self.end.to_shapely])
        return self._shapely_shape

    def point_projection(self, point: Coord) -> Coord:
        x1, y1 = self.start.xy
        x2, y2 = point.xy

        # slopes
        m = self.slope
        l = -1 / m

        # line equations intersections
        x = (y2 - y1 + m * x1 - l * x2) / (m - l)
        y = l * (x - x2) + y2
        return Coord(x, y)

    def linsplit(self, amount: int) -> List[Coord]:
        if amount == 0:
            return []

        if amount == 1:
            return [self.midpoint]

        step_length = self.length / (amount - 1)
        return [self.start.shifted(step_length * i, self.angle) for i in range(amount)]

    def linsplit_by_distance(self, distance: float) -> List[Coord]:
        return self.linsplit(amount=int(self.length / distance))

    def contains(self, point: Coord) -> bool:
        return abs(self.start.distance_to(point) + self.end.distance_to(point) - self.length) < 1e-5

    def sample(self) -> Coord:
        random_shift = random.uniform(0, self.length)
        return self.start.shifted(random_shift, self.angle)

    def __hash__(self):
        return hash(self.endpoints)

    def __str__(self):
        return f'Segment({self.start},{self.end})'

    def almost_equal(self, other: 'Segment') -> bool:
        return other.start.almost_equal(self.start) and other.end.almost_equal(self.end)

    def plot(self, color='green'):
        plt.plot([self.start.x, self.end.x], [self.start.y, self.end.y], color=color, zorder=10)
