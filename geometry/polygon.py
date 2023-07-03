from typing import List

import matplotlib.pyplot as plt
import shapely
from shapely.geometry.base import BaseGeometry

from geometry.coord import Coord
from geometry.entity import Entity
from geometry.segment import Segment


class Polygon(Entity):
    def __init__(self, coords: List[Coord]) -> None:
        if coords[-1] == coords[0]:
            coords = coords[:-1]

        self._coords = coords
        self._segments = [Segment(c1, c2) for c1, c2 in zip(coords[:-1], coords[1:])] \
                         + [Segment(coords[-1], coords[0])]
        self._perimeter = sum([segment.length for segment in self.segments])
        self._shapely_polygon = None

    @property
    def coords(self) -> List[Coord]:
        return self._coords

    @property
    def segments(self) -> List[Segment]:
        return self._segments

    @property
    def perimeter(self) -> float:
        return self._perimeter

    @property
    def to_shapely(self) -> BaseGeometry:
        if self._shapely_polygon is None:
            self._shapely_polygon = shapely.geometry.polygon.Polygon([coord.xy for coord in self.coords])
        return self._shapely_polygon

    def from_shapely(self, shapely_polygon: shapely.geometry.polygon.Polygon) -> 'Polygon':
        return Polygon.polygon_from_shapely(shapely_polygon)

    @classmethod
    def polygon_from_shapely(cls, shapely_polygon: shapely.geometry.polygon.Polygon) -> 'Polygon':
        return Polygon([Coord(x, y) for x, y in shapely_polygon.exterior.coords])

    def linsplit(self, amount: int) -> List[Coord]:
        segments_linsplits = [s.linsplit(round(amount * (s.length / self.perimeter))) for s in self.segments]
        segments_linsplits = list(set([item for sublist in segments_linsplits for item in sublist]))
        return segments_linsplits

    def linsplit_by_distance(self, distance: float) -> List[Coord]:
        segments_linsplits = [segment.linsplit_by_distance(distance) for segment in self.segments]
        segments_linsplits = list(set([item for sublist in segments_linsplits for item in sublist]))
        return segments_linsplits

    def __eq__(self, other: 'Polygon') -> bool:
        return len(self.coords) == len(other.coords) and all([c1 == c2 for c1, c2 in zip(self.coords, other.coords)])

    def __str__(self) -> str:
        return f'Polygon({self.coords})'

    def plot(self, color: str = 'blue') -> None:
        plt.plot([p.x for p in self.coords + [self.coords[0]]], [p.y for p in self.coords + [self.coords[0]]],
                 color=color, zorder=1)
