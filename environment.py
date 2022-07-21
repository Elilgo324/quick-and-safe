import time
from random import randint, seed
from typing import List, Tuple, Dict, Union

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from shapely.geometry import Point, Polygon, LineString


class Environment:
    def __init__(self, num_targets=10, num_no_entrances=10, num_threats=5, x_range=10_000, y_range=10_000,
                 seed_value=42) -> None:
        self._seed_value = seed_value
        seed(self._seed_value)

        # dimensions
        self._x_range = x_range
        self._y_range = y_range

        # entities and targets
        self._no_entrances = self._create_entities(num_no_entrances, (self._x_range / 100, self._x_range / 10))
        self._no_entrances_shapes = [ne['shape'] for ne in self._no_entrances]

        self._threats = self._create_entities(num_threats, (self._x_range / 10, self._x_range / 5))
        self._threats_shapes = [threat['shape'] for threat in self._threats]

        self._targets = self._create_targets(num_targets)
        self._targets_names = [f'({target.x},{target.y})' for target in self._targets]

    @property
    def x_range(self) -> int:
        return self._x_range

    @property
    def y_range(self) -> int:
        return self._y_range

    @property
    def no_entrances(self) -> List[Dict[str, Union[Point, float, Polygon]]]:
        return self._no_entrances

    @property
    def no_entrances_shapes(self) -> List[Polygon]:
        return self._no_entrances_shapes

    @property
    def threats(self) -> List[Dict[str, Union[Point, float, Polygon]]]:
        return self._threats

    @property
    def threats_shapes(self) -> List[Polygon]:
        return self._threats_shapes

    @property
    def targets(self) -> List[Point]:
        return self._targets

    @property
    def targets_names(self) -> List[str]:
        return self._targets_names

    def is_legal_point(self, point: Point) -> bool:
        for obstacle in self._no_entrances:
            if obstacle['shape'].contains(point):
                return False
        return True

    def is_legal_edge(self, p1: Point, p2: Point) -> bool:
        line = LineString([p1, p2])
        for ne in self._no_entrances_shapes:
            if line.intersects(ne):
                return False
        return True

    def _create_entities(self, num_entities: int, radius_range: Tuple[float, float]) \
            -> List[Dict[str, Union[Point, float, Polygon]]]:
        entities_points = [Point(randint(0, self._x_range), randint(0, self._y_range))
                           for _ in range(num_entities)]

        rads = [randint(*radius_range) for _ in entities_points]

        return [{'center': point, 'radius': radius, 'shape': point.buffer(radius)}
                for point, radius in zip(entities_points, rads)]

    def _create_targets(self, num_targets: int) -> List[Point]:
        # create targets out of no entrance zones
        targets = []
        while len(targets) < num_targets:
            potential_target = Point(randint(0, self._x_range), randint(0, self._y_range))
            if self.is_legal_point(potential_target):
                targets.append(potential_target)
        return targets

    def sample(self) -> Point:
        rand_point = Point(randint(0, self._x_range), randint(0, self._y_range))
        while not self.is_legal_point(rand_point):
            rand_point = Point(randint(0, self._x_range), randint(0, self._y_range))
        return rand_point

    def plot(self) -> None:
        plt.figure(figsize=(10, 10))
        plt.title(f'environment of seed {self._seed_value}', fontsize=20)

        # plot no entrances
        for ne in self._no_entrances:
            X, Y = ne['shape'].exterior.xy
            plt.scatter(ne['center'].x, ne['center'].y, s=30, color='black', zorder=3)
            plt.scatter(ne['center'].x, ne['center'].y, s=20, color='blue', zorder=4)
            plt.plot(X, Y, color='blue')

        # plot threats
        for threat in self._threats:
            X, Y = threat['shape'].exterior.xy
            plt.scatter(threat['center'].x, threat['center'].y, s=30, color='black', zorder=3)
            plt.scatter(threat['center'].x, threat['center'].y, s=20, color='red', zorder=4)
            plt.plot(X, Y, color='red')

        # plot targets
        for target in self._targets:
            plt.scatter(target.x, target.y, color='black', zorder=9, s=100)
            plt.scatter(target.x, target.y, color='gold', zorder=10, s=80)

        # plot legend
        plt.legend(handles=[mpatches.Patch(color='gold', label=f'{len(self._targets)} targets'),
                            mpatches.Patch(color='blue', label=f'{len(self._no_entrances)} no entrance zones'),
                            mpatches.Patch(color='red', label=f'{len(self._threats)} threats')], ncol=3,
                   loc='upper center')
