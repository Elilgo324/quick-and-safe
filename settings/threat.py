import math
from random import randint
from typing import List, Tuple
import matplotlib.pyplot as plt

from shapely.geometry import Point, Polygon

from algorithms.geometric import calculate_directional_angle_of_line
from settings.coord import Coord

ANGLE_STEP = math.pi / 20
BUFFER_RESOLUTION = 20
EPSILON = 0.1


def _compute_path_length(path: List[Coord]) -> float:
    return sum([c1.distance(c2) for c1, c2 in zip(path[:-1], path[1:])])


class Threat:
    def __init__(self, center: Coord, radius: float) -> None:
        self._center = center
        self._radius = radius
        self._polygon = center.buffer(radius, resolution=BUFFER_RESOLUTION)
        self._boundary = None

    @property
    def center(self) -> Coord:
        return self._center

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def polygon(self) -> Polygon:
        return self._polygon

    @property
    def boundary(self) -> List[Coord]:
        if self._boundary is None:
            X, Y = self.polygon.exterior.coords.xy
            self._boundary = [Coord(x, y) for x, y in zip(list(X), list(Y))]
        return self._boundary

    def get_boundary_between(self, start: Coord, end: Coord) -> List[Coord]:
        angle1 = calculate_directional_angle_of_line(start=self.center, end=start)
        angle2 = calculate_directional_angle_of_line(start=self.center, end=end)

        small_angle = min(angle1, angle2)
        great_angle = max(angle1, angle2)

        # counterclockwise boundary
        boundary1 = []
        angle = small_angle
        while angle < great_angle:
            boundary1.append(self.center.shift(self.radius + EPSILON, angle))
            angle += ANGLE_STEP
        boundary1.append(self.center.shift(self.radius + EPSILON, great_angle))

        # clockwise boundary
        boundary2 = []
        angle = great_angle
        while angle > small_angle:
            boundary2.append(self.center.shift(self.radius + EPSILON, angle))
            angle -= ANGLE_STEP
        boundary2.append(self.center.shift(self.radius + EPSILON, small_angle))

        # choose shorter boundary
        return min([boundary1, boundary2], key=_compute_path_length)

    def get_buffered_boundary(self, buffer: float = 1) -> List[Coord]:
        X, Y = self.center.buffer(self.radius + buffer, resolution=BUFFER_RESOLUTION).exterior.coords.xy
        return [Coord(x, y) for x, y in zip(list(X), list(Y))]

    @classmethod
    def generate_random_threat(cls, environment_range: Tuple[int, int], radius_range: Tuple[int, int] = (100, 200)) \
            -> 'Threat':
        rand_radius = randint(*radius_range)
        x_range, y_range = environment_range
        rand_center = Coord(randint(rand_radius, x_range - rand_radius), randint(rand_radius, y_range - rand_radius))
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
                if threat.buffer(5).intersects(new_threat.polygon.buffer(5)):
                    is_intersecting = True
                    break

        return new_threat

    def plot(self) -> None:
        plt.plot([p.x for p in self.boundary], [p.y for p in self.boundary], color='red', zorder=1)
        plt.scatter(self.center.x, self.center.y, s=20, color='black', zorder=1)
        plt.scatter(self.center.x, self.center.y, s=10, color='red', zorder=2)
