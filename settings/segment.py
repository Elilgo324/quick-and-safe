from typing import Tuple

from algorithms.geometric import calculate_directional_angle_of_line
from settings.coord import Coord


class Segment:
    def __init__(self, start: Coord, end: Coord) -> None:
        self._start = start
        self._end = end

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
    def length(self) -> Coord:
        return self._start.distance(self._end)

    @property
    def angle(self) -> float:
        return calculate_directional_angle_of_line(self.start, self.end)

    @property
    def midpoint(self) -> Coord:
        return Coord((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2)

    def __hash__(self):
        return hash(self.endpoints)

    def __str__(self):
        return f'Segment({self.start},{self.end})'
