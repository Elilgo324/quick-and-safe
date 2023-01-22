import math
from random import randint
from typing import List, Tuple
import matplotlib.pyplot as plt

from shapely.geometry import Polygon, LineString

from geometry.geometric import calculate_directional_angle_of_line
from geometry.coord import Coord
from geometry.entity import Entity
from geometry.path import Path


class Circle(Entity):
    BUFFER_RESOLUTION = 40
    ANGLE_STEP = math.pi / BUFFER_RESOLUTION
    EPSILON = 1

    def __init__(self, center: Coord, radius: float) -> None:
        self._center = center
        self._radius = radius
        self._inner_polygon = center.to_shapely.buffer(radius, resolution=Circle.BUFFER_RESOLUTION)
        self._outer_polygon = center.to_shapely.buffer(radius + Circle.EPSILON, resolution=Circle.BUFFER_RESOLUTION)
        self._boundary = None

    @property
    def center(self) -> Coord:
        return self._center

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def inner_polygon(self) -> Polygon:
        return self._inner_polygon

    @property
    def outer_polygon(self) -> Polygon:
        return self._outer_polygon

    @property
    def to_shapely(self) -> Polygon:
        return self._inner_polygon

    def compute_path_risk(self, path: Path) -> float:
        return sum([self.inner_polygon.intersection(segment.to_shapely).length for segment in path.segments])

    @property
    def boundary(self) -> List[Coord]:
        if self._boundary is None:
            X, Y = self.outer_polygon.exterior.coords.xy
            self._boundary = [Coord(x, y) for x, y in zip(list(X), list(Y))]
        return self._boundary

    def get_boundary_between(self, start: Coord, end: Coord) -> List[Coord]:
        angle1 = calculate_directional_angle_of_line(start=self.center, end=start)
        angle2 = calculate_directional_angle_of_line(start=self.center, end=end)

        small_angle = min(angle1, angle2)
        great_angle = max(angle1, angle2)

        boundary = []

        # if shorter boundary is counterclockwise
        if great_angle - small_angle <= math.pi:
            angle = small_angle
            while angle < great_angle:
                boundary.append(self.center.shifted(self.radius + Circle.EPSILON, angle))
                angle += Circle.ANGLE_STEP
            boundary.append(self.center.shifted(self.radius + Circle.EPSILON, great_angle))

        # if shorter boundary is clockwise
        else:
            angle = great_angle
            while angle > small_angle:
                boundary.append(self.center.shifted(self.radius + Circle.EPSILON, angle))
                angle -= Circle.ANGLE_STEP
            boundary.append(self.center.shifted(self.radius + Circle.EPSILON, small_angle))

        return boundary[::-1] if not boundary[0].almost_equal(start, epsilon=Circle.EPSILON) else boundary

    @classmethod
    def generate_random_threat(cls, environment_range: Tuple[int, int], radius_range: Tuple[int, int] = (100, 200)) \
            -> 'Circle':
        rand_radius = randint(*radius_range)
        x_range, y_range = environment_range
        rand_center = Coord(randint(rand_radius, x_range - rand_radius), randint(rand_radius, y_range - rand_radius))
        return Circle(center=rand_center, radius=rand_radius)

    @classmethod
    def generate_non_intersecting_random_threat(cls, threats_polygons: List[Polygon],
                                                environment_range: Tuple[int, int],
                                                radius_range: Tuple[int, int] = (100, 200)) -> 'Circle':
        new_threat = None

        is_intersecting = True
        while is_intersecting:
            is_intersecting = False
            new_threat = Circle.generate_random_threat(environment_range, radius_range)

            for threat in threats_polygons:
                if threat.buffer(5).intersects(new_threat.inner_polygon.buffer(5)):
                    is_intersecting = True
                    break

        return new_threat

    def plot(self) -> None:
        plt.plot([p.x for p in self.boundary], [p.y for p in self.boundary], color='red', zorder=1)
        plt.scatter(self.center.x, self.center.y, s=20, color='black', zorder=1)
        plt.scatter(self.center.x, self.center.y, s=10, color='red', zorder=2)
