from typing import List

import matplotlib.pyplot as plt
from shapely.geometry import LineString

from geometry.coord import Coord
from geometry.entity import Entity
from geometry.segment import Segment


class Path(Entity):
    def __init__(self, coords: List[Coord]) -> None:
        self._coords = coords
        self._segments = [Segment(c1, c2) for c1, c2 in zip(coords[:-1], coords[1:])]
        self._length = None
        self._shapely_shape = None

    @property
    def to_shapely(self) -> LineString:
        if self._shapely_shape is None:
            self._shapely_shape = LineString([c.to_shapely for c in self.coords])
        return self._shapely_shape

    def from_shapely(self, shapely_linestring: LineString) -> 'Path':
        return Path([Coord(*coord.xy) for coord in shapely_linestring.coords])

    @property
    def reversed(self) -> 'Path':
        return self.__init__(self.coords[::-1])

    @property
    def coords(self) -> List[Coord]:
        return self._coords

    @property
    def segments(self) -> List[Segment]:
        return self._segments

    @property
    def source(self) -> Coord:
        return self.coords[0]

    @property
    def target(self) -> Coord:
        return self.coords[-1]

    @property
    def endpoints(self) -> List[Coord]:
        return [self.source, self.target]

    @property
    def length(self) -> float:
        if self._length is None:
            self._length = Path.compute_path_length(self.coords)
        return self._length

    @property
    def perimeter(self) -> float:
        return self.length

    @classmethod
    def compute_path_length(cls, path: List[Coord]) -> float:
        return sum([c1.distance_to(c2) for c1, c2 in zip(path[:-1], path[1:])])

    def __eq__(self, other: 'Path') -> bool:
        return all([c1 == c2 for c1, c2 in zip(self.coords, other.coords)]) \
            and all([e1 == e2 for e1, e2 in zip(self.segments, other.segments)])

    def __getitem__(self, idx: int) -> 'Coord':
        return self.coords[idx]

    @classmethod
    def concat_paths(cls, path1: 'Path', path2: 'Path') -> 'Path':
        return cls(path1.coords + path2.coords)

    def __str__(self) -> str:
        return f'Path({self.coords})'

    def plot(self, color='green') -> None:
        plt.plot([c.x for c in self.coords], [c.y for c in self.coords], color=color, zorder=10)
        plt.scatter([c.x for c in self.coords], [c.y for c in self.coords], s=20, color='black', zorder=10)
        plt.scatter([c.x for c in self.coords], [c.y for c in self.coords], s=10, color=color, zorder=11)
        plt.scatter([c.x for c in self.endpoints], [c.y for c in self.endpoints], s=10, color='orange', zorder=12)
