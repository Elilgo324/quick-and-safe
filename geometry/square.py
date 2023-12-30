import math
from typing import List

import matplotlib.pyplot as plt
import shapely
from shapely.geometry.base import BaseGeometry

from geometry.coord import Coord
from geometry.entity import Entity
from geometry.polygon import Polygon
from geometry.segment import Segment


class Square(Polygon):
    def __init__(self, center: Coord, edge_length: float) -> None:
        self._center = center
        half_diagonal = 0.5 * math.sqrt(2 * edge_length**2)
        coords = [center.shifted(half_diagonal, 0.25*math.pi),
                  center.shifted(half_diagonal, 0.75*math.pi),
                  center.shifted(half_diagonal, 1.25*math.pi),
                  center.shifted(half_diagonal, 1.75*math.pi)]
        super().__init__(coords)

    @property
    def center(self) -> Coord:
        return self._center

    @property
    def __str__(self) -> str:
        return f'Square({self.coords})'

    def plot(self, color: str = 'blue') -> None:
        plt.plot([p.x for p in self.coords + [self.coords[0]]], [p.y for p in self.coords + [self.coords[0]]],
                 color=color, zorder=1)
