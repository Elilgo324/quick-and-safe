import time
from random import randint, uniform, seed
from typing import List, Tuple, Dict, Union

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from shapely.geometry import Point, Polygon

from prob_roadmap import ProbRoadmap


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

        self._graph = None

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
        self._targets = []
        while len(self._targets) < num_targets:
            potential_target = Point(randint(0, self._x_range), randint(0, self._y_range))
            if not self._target_is_in_obstacle(potential_target):
                self._targets.append(potential_target)

    def create_roadmap(self, num_iterations: int = 1000) -> None:
        prm = ProbRoadmap(self._x_range, self._y_range, [ne['shape'] for ne in self._no_entrances])
        prm.add_points(self._targets)
        prm.extend_iterations(num_iterations)
        self._graph = prm.graph

    def plot_environment(self) -> None:
        plt.figure(figsize=(10, 10))
        plt.title(f'roadmap of size {len(self._graph.nodes)} nodes and {len(self._graph.edges)} '
                  f'edges (seed {self._seed_value})', fontsize=20)

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

        # plot roadmap
        if self._graph is not None:
            for _, _, e_data in self._graph.edges(data=True):
                x1, x2, y1, y2 = e_data['x1'], e_data['x2'], e_data['y1'], e_data['y2']
                plt.plot([x1, x2], [y1, y2], color='green')
                plt.scatter([x1, x2], [y1, y2], color='black', s=60, zorder=7)
                plt.scatter([x1, x2], [y1, y2], color='gray', s=50, zorder=8)

        # plot targets
        for target in self._targets:
            plt.scatter(target.x, target.y, color='black', zorder=9, s=100)
            plt.scatter(target.x, target.y, color='gold', zorder=10, s=80)

        plt.legend(handles=[mpatches.Patch(color='gold', label=f'{len(self._targets)} targets'),
                            mpatches.Patch(color='blue', label=f'{len(self._no_entrances)} no entrance zones'),
                            mpatches.Patch(color='red', label=f'{len(self._threats)} threats')])
        plt.show()


if __name__ == '__main__':
    env = Environment()
    env.create_roadmap(num_iterations=1000)
    env.plot_environment()
    graph = env._graph
    start = time.time()
    nx.floyd_warshall(graph)
    print(time.time() - start)
