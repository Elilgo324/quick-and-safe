import math
from typing import List, Tuple, Dict

from shapely.geometry import Point
from heapq import nsmallest

from roadmap.roadmap import Roadmap
from settings.environment import Environment


class PRM(Roadmap):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        # neighborhood consts
        self._neighborhood_k = 10
        self._neighborhood_dist = 1000

    def _k_neighborhood(self, point: Point) -> List[Tuple[str, Dict]]:
        def _k_nearest_key(point_xy) -> float:
            _, xy = point_xy
            dist = (xy['x'] - point.x) ** 2 + (xy['y'] - point.y) ** 2
            return dist if dist > 0 else math.inf

        k_nearest_nodes = nsmallest(self._neighborhood_k, self._graph.nodes(data=True), key=_k_nearest_key)
        return k_nearest_nodes

    def _dist_neighborhood(self, point: Point) -> List[Tuple[str, Dict]]:
        neighborhood_nodes = []
        for node_name, xy in self._graph.nodes(data=True):
            dist = ((xy['x'] - point.x) ** 2 + (xy['y'] - point.y) ** 2) ** 0.5
            if dist < self._neighborhood_dist:
                neighborhood_nodes.append((node_name, xy))

        return neighborhood_nodes

    def add_samples(self, num_samples: int, neighborhood_type: str = 'k') -> None:
        samples = [self._env.sample() for _ in range(num_samples)]

        # add nodes to graph
        self._add_points(samples)

        # add legal edges to graph
        for sample in samples:
            self._perform_connections(sample, neighborhood_type)

    def _perform_connections(self, sample: Point, neighborhood_type: str) -> None:
        # add sample to graph
        sample_name = f'({sample.x},{sample.y})'
        self._graph.add_node(sample_name, x=sample.x, y=sample.y)

        # find near nodes to connect
        if neighborhood_type == 'k':
            near_nodes = self._k_neighborhood(sample)
        else:
            near_nodes = self._dist_neighborhood(sample)

        # add illegal edges with near group
        for node_name, node_data in near_nodes:
            x1, y1, x2, y2 = sample.x, sample.y, node_data['x'], node_data['y']
            if self._environment.is_legal_edge(sample, Point(x2, y2)):
                weight = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                self._graph.add_edge(sample_name, node_name, x1=x1, x2=x2, y1=y1, y2=y2, weight=weight)