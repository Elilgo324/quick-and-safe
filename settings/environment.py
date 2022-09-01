import time
from random import randint, seed
from typing import List, Tuple, Dict, Union

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import Point, Polygon, LineString

from threat import Threat


class Environment:
    def __init__(self, num_targets: int = 10, num_threats: int = 10,
                 env_range: (int, int) = (1000, 1000), seed_value: int = 42) -> None:
        self._seed_value = seed_value
        seed(self._seed_value)

        self._x_range, self._y_range = env_range

        self._threats, self._threats_polygons, self._targets = [], [], []

        self._create_disjoint_threats(num_threats)
        self._create_targets(num_targets)

    @property
    def x_range(self) -> int:
        return self._x_range

    @property
    def y_range(self) -> int:
        return self._y_range

    @property
    def threats(self) -> List[Threat]:
        return self._threats

    @property
    def threats_polygons(self) -> List[Polygon]:
        return self._threats_polygons

    @property
    def targets(self) -> List[Point]:
        return self._targets

    def is_safe_point(self, point: Point) -> bool:
        for threat in self.threats_polygons:
            if threat.contains(point):
                return False
        return True

    def is_safe_edge(self, p1: Point, p2: Point) -> bool:
        line = LineString([p1, p2])
        for threat in self.threats_polygons:
            if line.intersects(threat):
                return False
        return True

    def _create_threats(self, num_threats: int) -> None:
        self._threats = [Threat.generate_random_threat((self.x_range, self.y_range)) for _ in range(num_threats)]
        self._threats_polygons = [threat.polygon for threat in self._threats]

    def _create_disjoint_threats(self, num_threats: int) -> None:
        for _ in range(num_threats):
            new_threat = Threat.generate_non_intersecting_random_threat(
                self.threats_polygons, (self.x_range, self.y_range))
            self._threats.append(new_threat)
            self._threats_polygons.append(new_threat.polygon)

    def _create_targets(self, num_targets: int) -> None:
        # create targets out of threats
        self._targets = [self.sample() for _ in range(num_targets)]

    def sample(self) -> Point:
        rand_point = Point(randint(0, self._x_range), randint(0, self._y_range))
        while not self.is_safe_point(rand_point):
            rand_point = Point(randint(0, self._x_range), randint(0, self._y_range))
        return rand_point

    def plot(self) -> None:
        plt.figure(figsize=(10, 10))
        plt.style.use('seaborn-whitegrid')
        plt.grid(True)
        plt.axis('equal')

        # plot threats
        for threat in self._threats:
            X, Y = threat.polygon.exterior.xy
            plt.scatter(threat.center.x, threat.center.y, s=20, color='black', zorder=3)
            plt.scatter(threat.center.x, threat.center.y, s=10, color='red', zorder=4)
            plt.plot(X, Y, color='red')

        # plot targets
        for target in self._targets:
            plt.scatter(target.x, target.y, color='black', zorder=9, s=30)
            plt.scatter(target.x, target.y, color='gold', zorder=10, s=20)