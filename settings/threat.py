from random import randint
from typing import List, Tuple

from shapely.geometry import Point, Polygon

BUFFER_RESOLUTION = 4


class Threat:
    def __init__(self, center: Point, radius: float) -> None:
        self._center = center
        self._radius = radius
        self._polygon = center.buffer(radius, resolution=BUFFER_RESOLUTION)
        self._boundary = None

    @property
    def center(self) -> Point:
        return self._center

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def polygon(self) -> Polygon:
        return self._polygon

    @property
    def boundary(self) -> List[Point]:
        if self._boundary is None:
            X, Y = self.polygon.exterior.coords.xy
            self._boundary = [Point(x, y) for x, y in zip(list(X), list(Y))]
        return self._boundary

    def get_buffered_boundary(self, buffer: float = 1) -> List[Point]:
        X, Y = self.center.buffer(self.radius + buffer, resolution=BUFFER_RESOLUTION).exterior.coords.xy
        return [Point(x, y) for x, y in zip(list(X), list(Y))]

    @classmethod
    def generate_random_threat(cls, environment_range: Tuple[int, int], radius_range: Tuple[int, int] = (100, 200)) \
            -> 'Threat':
        rand_radius = randint(*radius_range)
        x_range, y_range = environment_range
        rand_center = Point(randint(rand_radius, x_range - rand_radius), randint(rand_radius, y_range - rand_radius))
        return Threat(center=rand_center, radius=rand_radius)

    @classmethod
    def generate_non_intersecting_random_threat(cls, threats_polygons: List[Polygon],
                                                environment_range: Tuple[int, int],
                                                radius_range: Tuple[int, int] = (100, 200)) -> 'Threat':
        new_threat = None

        is_intersecting = True
        while is_intersecting:
            is_intersecting = False
            new_threat = Threat.generate_random_threat(environment_range, radius_range)

            for threat in threats_polygons:
                if threat.intersects(new_threat.polygon):
                    is_intersecting = True
                    break

        return new_threat
