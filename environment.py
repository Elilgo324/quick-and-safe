import time
from random import randint, uniform, seed
from typing import List, Tuple, Dict, Union

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from shapely.geometry import Point, Polygon

from prm import PRM


class Environment:
    def __init__(self, num_targets=10, num_no_entrances=10, num_threats=5, x_range=10_000, y_range=10_000,
                 seed_value=42) -> None:
        self._seed_value = seed_value
        seed(self._seed_value)

        self._x_range = x_range
        self._y_range = y_range

        self._no_entrances = self._create_entities(num_no_entrances, (self._x_range / 100, self._x_range / 10))
        self._threats = self._create_entities(num_threats, (self._x_range / 10, self._x_range / 5))

        self._create_targets(num_targets)

    @property
    def x_range(self):
        return self._x_range

    @property
    def y_range(self):
        return self._y_range

    @property
    def no_entrances(self):
        return self._no_entrances

    @property
    def threats(self):
        return self._threats

    @property
    def targets(self):
        return self._targets

    def _create_entities(self, num_entities: int, radius_range: Tuple[float, float]) \
            -> List[Dict[str, Union[Point, float, Polygon]]]:
        entities_points = [Point(randint(0, self._x_range), randint(0, self._y_range))
                           for _ in range(num_entities)]

        rads = [randint(*radius_range) for _ in entities_points]

        return [{'center': point, 'radius': radius, 'shape': point.buffer(radius)}
                for point, radius in zip(entities_points, rads)]

    def _target_is_in_obstacle(self, target: Point) -> bool:
        for obstacle in self._no_entrances:
            if obstacle['shape'].contains(target):
                return True
        return False

    def _create_targets(self, num_targets: int) -> None:
        # create targets out of no entrance zones
        self._targets = []
        while len(self._targets) < num_targets:
            potential_target = Point(randint(0, self._x_range), randint(0, self._y_range))
            if not self._target_is_in_obstacle(potential_target):
                self._targets.append(potential_target)

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
                            mpatches.Patch(color='red', label=f'{len(self._threats)} threats')], ncol=3, loc='upper center')


if __name__ == '__main__':
    # create environment
    env = Environment()
    env.plot()

    # create roadmap
    prm = PRM(env.x_range, env.y_range, [ne['shape'] for ne in env.no_entrances], env.targets)
    prm.extend_iterations(100)
    prm.plot()
    plt.show()
