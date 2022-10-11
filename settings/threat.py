import math
from random import randint
from typing import List, Tuple
import matplotlib.pyplot as plt

from shapely.geometry import Point, Polygon

from algorithms.geometric import calculate_directional_angle_of_line
from settings.coord import Coord


def _compute_path_length(path: List[Coord]) -> float:
    return sum([c1.distance(c2) for c1, c2 in zip(path[:-1], path[1:])])


class Threat:
    ANGLE_STEP = math.pi / 20
    BUFFER_RESOLUTION = 20
    EPSILON = 0.03

    def __init__(self, center: Coord, radius: float) -> None:
        """Init threat by center and radius

        :param center: the center of the threat
        :param radius: the radius of the threat
        """
        self._center = center
        self._radius = radius
        self._polygon = center.buffer(radius, resolution=Threat.BUFFER_RESOLUTION)
        self._boundary = None

    @property
    def center(self) -> Coord:
        """The center of the threat

        :return: the center of the threat
        """
        return self._center

    @property
    def radius(self) -> float:
        """The radius of the threat

        :return: the radius of the threat
        """
        return self._radius

    @property
    def polygon(self) -> Polygon:
        """The polygon of the threat

        :return: the polygon of the threat
        """
        return self._polygon

    @property
    def boundary(self) -> List[Coord]:
        """The boundary of the threat

        :return: the boundary of the threat
        """
        if self._boundary is None:
            X, Y = self.polygon.exterior.coords.xy
            self._boundary = [Coord(x, y) for x, y in zip(list(X), list(Y))]
        return self._boundary

    def get_boundary_between(self, start: Coord, end: Coord) -> List[Coord]:
        """Get the boundary between start and end coordinates

        :param start: start coord
        :param end: end coord
        :return: the boundary between start and end coords
        """
        angle1 = calculate_directional_angle_of_line(start=self.center, end=start)
        angle2 = calculate_directional_angle_of_line(start=self.center, end=end)

        small_angle = min(angle1, angle2)
        great_angle = max(angle1, angle2)

        # counterclockwise boundary
        boundary1 = []
        angle = small_angle
        while angle < great_angle:
            boundary1.append(self.center.shift(self.radius, angle))
            angle += Threat.ANGLE_STEP
        boundary1.append(self.center.shift(self.radius, great_angle))

        # clockwise boundary
        boundary2 = []
        angle = great_angle
        while angle > small_angle:
            boundary2.append(self.center.shift(self.radius, angle))
            angle -= Threat.ANGLE_STEP
        boundary2.append(self.center.shift(self.radius, small_angle))

        # choose shorter boundary
        return min([boundary1, boundary2], key=_compute_path_length)

    @classmethod
    def generate_random_threat(cls, environment_range: Tuple[int, int], radius_range: Tuple[int, int] = (100, 200)) \
            -> 'Threat':
        """Generates a random threat

        :param environment_range: the range of the environment
        :param radius_range: the range of the radius
        :return: a random threat
        """
        rand_radius = randint(*radius_range)
        x_range, y_range = environment_range
        rand_center = Coord(randint(rand_radius, x_range - rand_radius), randint(rand_radius, y_range - rand_radius))
        return Threat(center=rand_center, radius=rand_radius)

    @classmethod
    def generate_non_intersecting_random_threat(cls, threats_polygons: List[Polygon],
                                                environment_range: Tuple[int, int],
                                                radius_range: Tuple[int, int] = (100, 200)) -> 'Threat':
        """Generates a random threat that does not intersect given threats list

        :param threats_polygons: the threats polygons
        :param environment_range: the range of the environment
        :param radius_range: the range of the radius
        :return: a random threat that does not intersect given threats list
        """
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
        """Plots the threat"""
        plt.plot([p.x for p in self.boundary], [p.y for p in self.boundary], color='red', zorder=1)
        plt.scatter(self.center.x, self.center.y, s=20, color='black', zorder=1)
        plt.scatter(self.center.x, self.center.y, s=10, color='red', zorder=2)
