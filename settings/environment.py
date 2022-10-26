import time
from random import randint, seed
from typing import List, Tuple, Dict, Union

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import Polygon, LineString

from settings.coord import Coord
from settings.threat import Threat


class Environment:
    def __init__(self, source: Coord, target: Coord, num_threats: int = 10, env_range: (int, int) = (1000, 1000),
                 seed_value: int = 42) -> None:
        """Init environment

        :param source: source of query
        :param target: target of query
        :param num_threats: num of threats in the environment
        :param env_range: the range of the environment
        :param seed_value: seed of the environment's threats map
        """
        self._seed_value = seed_value
        seed(self._seed_value)

        self._source = source
        self._target = target
        self._x_range, self._y_range = env_range

        self._threats = []
        self._create_disjoint_threats(num_threats)

    @property
    def x_range(self) -> int:
        """The x range of the environment

        :return: the x range of the environment
        """
        return self._x_range

    @property
    def y_range(self) -> int:
        """The y range of the environment

        :return: the y range of the environment
        """
        return self._y_range

    @property
    def threats(self) -> List[Threat]:
        """The threats in the environment

        :return: the threats in the environment
        """
        return self._threats

    @property
    def threats_polygons(self) -> List[Polygon]:
        """The threats polygons in the environment

        :return: the threats polygons in the environment
        """
        return [threat.polygon for threat in self._threats]

    @property
    def source(self) -> Coord:
        """The source coord

        :return: the source coord
        """
        return self._source

    @property
    def target(self) -> Coord:
        """The target coord

        :return: the target coord
        """
        return self._target

    @property
    def endpoints(self) -> List[Coord]:
        """The source and the target

        :return: the source and the target
        """
        return [self._source, self._target]

    def is_safe_point(self, point: Coord) -> bool:
        """Checks if point is inside threat

        :param point: a point
        :return: if the point is inside threat
        """
        for threat in self.threats_polygons:
            if threat.contains(point):
                return False
        return True

    def is_safe_edge(self, u: Coord, v: Coord) -> bool:
        """Checks if an edge uv intersects threat

        :param u: the first coord of the edge
        :param v: the second coord of the edge
        :return: if the edge does not intersect threat
        """
        line = LineString([u, v])
        for threat_polygon in self.threats_polygons:
            if line.intersects(threat_polygon):
                return False
        return True

    def _create_threats(self, num_threats: int) -> None:
        """Creates the random threats of the environment

        :param num_threats: the number of the threats to generate
        """
        self._threats = [Threat.generate_random_threat((self.x_range, self.y_range)) for _ in range(num_threats)]

    def _create_disjoint_threats(self, num_threats: int) -> None:
        """Creates the random non-intersecting threats of the environment

        :param num_threats: the number of the threats to generate
        """
        for _ in range(num_threats):
            new_threat = Threat.generate_non_intersecting_random_threat(
                self.threats_polygons, (self.x_range, self.y_range))
            self._threats.append(new_threat)

    def compute_segment_attributes(self, u: Coord, v: Coord) -> Dict[str, float]:
        """Computes the attributes of a given edge uv

        :param u: the first point of the edge
        :param v: the second point of the edge
        :return: the attributes of the segment
        """
        segment = LineString([u, v])
        return {'length': segment.length,
                'risk': sum([threat.compute_path_risk([u, v]) for threat in self.threats])}

    def compute_path_attributes(self, path: List[Coord]) -> Dict[str, float]:
        """Computes the attributes of a given path

        :param path: a path
        :return: the attributes of the path
        """
        segments_attributes = [self.compute_segment_attributes(u, v) for u, v in zip(path[:-1], path[1:])]
        return {'length': sum(attr['length'] for attr in segments_attributes),
                'risk': sum(attr['risk'] for attr in segments_attributes)}

    def sample(self, is_safe_sample=True) -> Coord:
        """Samples point in the environment

        :param is_safe_sample: if sample only safe points
        :return: a sample in the environment
        """
        rand_point = Coord(randint(0, self._x_range), randint(0, self._y_range))
        while is_safe_sample and not self.is_safe_point(rand_point):
            rand_point = Coord(randint(0, self._x_range), randint(0, self._y_range))
        return rand_point

    def plot(self) -> None:
        """Plots the environment"""
        plt.figure(figsize=(10, 10))
        plt.style.use('seaborn-whitegrid')
        plt.grid(True)
        plt.axis('equal')

        # plot threats
        for threat in self._threats:
            threat.plot()

        # plot source and target
        for endpoint in [self._source, self._target]:
            plt.scatter(endpoint.x, endpoint.y, color='black', zorder=9, s=60)
            plt.scatter(endpoint.x, endpoint.y, color='gold', zorder=10, s=50)
