import math
from heapq import nsmallest
from typing import List

from environment.environment import Environment
from geometry.coord import Coord
from roadmaps.roadmap import Roadmap


class PRM(Roadmap):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        # neighborhood consts
        self._neighborhood_k = 10
        self._near_radius = 10

    def _near(self, point: Coord) -> List[Coord]:
        return [Coord(*p) for p in self.graph.nodes if Coord(*p).distance_to(point) < self._near_radius]

    def _k_neighborhood(self, point: Coord) -> List[Coord]:
        def _k_nearest_key(other) -> float:
            dist = Coord(*other).distance_to(point)
            # if distance is 0 it is the node itself
            return dist if dist > 0 else math.inf

        return [Coord(*p) for p in nsmallest(self._neighborhood_k, self._graph.nodes, key=_k_nearest_key)]

    def _perform_connections(self, sample: Coord) -> None:
        # find near nodes to connect
        near_nodes = self._k_neighborhood(sample)

        self._add_edges([(sample, node) for node in near_nodes])

    def add_samples(self, num_samples: int) -> None:
        samples = [self._environment.sample(is_safe_sample=False) for _ in range(num_samples)]

        # add nodes to graph
        self._add_points(samples)

        # add legal edges to graph
        for sample in samples:
            self._perform_connections(sample)
