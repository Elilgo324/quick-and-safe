import math
from typing import Tuple

from shapely.geometry import Point


class Coord(Point):
    @property
    def xy(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def shift(self, distance: float, angle: float) -> 'Coord':
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        return Coord(self.x + x, self.y + y)

    def __hash__(self):
        return hash(self.xy)

    def __str__(self):
        return f'Coord({self.x},{self.y})'