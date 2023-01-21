import math
from typing import Tuple

from shapely import LineString

from geometry.geometric import calculate_directional_angle_of_line
from geometry.coord import Coord
from geometry.entity import Entity


class Segment(Entity):
    def __init__(self, start: Coord, end: Coord) -> None:
        self._start = start
        self._end = end
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
    def length(self) -> float:
        return self._start.distance_to(self._end)

    @property
    def angle(self) -> float:
        if self._angle is None:
            self._angle = calculate_directional_angle_of_line(self.start, self.end)
        return self._angle

    @property
    def vertical_segment(self) -> 'Segment':
        if self._vertical_segment is None:
            self._vertical_segment = Segment(
                self.midpoint.shifted(self.length / 2, self.angle + math.pi / 2),
                self.midpoint.shifted(self.length / 2, self.angle - math.pi / 2)
            )
        return self._vertical_segment

    @property
    def midpoint(self) -> Coord:
        return Coord((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2)

    @property
    def to_shapely(self) -> LineString:
        if self._shapely_shape is None:
            self._shapely_shape = LineString([self.start.to_shapely, self.end.to_shapely])
        return self._shapely_shape

    def __hash__(self):
        return hash(self.endpoints)

    def __str__(self):
        return f'Segment({self.start},{self.end})'

    def almost_equal(self, other: 'Segment') -> bool:
        return other.start.almost_equal(self.start) and other.end.almost_equal(self.end)
