import math
from typing import List

from heapq import nsmallest

from roadmap.roadmap import Roadmap
from geometry.coord import Coord
from environment.environment import Environment


class PRM(Roadmap):
    def __init__(self, environment: Environment) -> None:
        """Init of PRM

        :param environment: the environment
        """
        super().__init__(environment)

        # neighborhood consts
        self._neighborhood_k = 10
        self._near_radius = 10

    def _near(self, point: Coord) -> List[Coord]:
        """Computes the near nodes of a given point

        :param point: the point
        :return: the near nodes of the point
        """
        return [Coord(*p) for p in self.graph.nodes if Coord(*p).distance(point) < self._near_radius]

    def _k_neighborhood(self, point: Coord) -> List[Coord]:
        """Computes the k neighborhood of the point

        :param point: the point
        :return: the k neighborhood of the point
        """

        def _k_nearest_key(other) -> float:
            dist = Coord(*other).distance(point)
            # if distance is 0 it is the node itself
            return dist if dist > 0 else math.inf

        return [Coord(*p) for p in nsmallest(self._neighborhood_k, self._graph.nodes, key=_k_nearest_key)]

    def _perform_connections(self, sample: Coord) -> None:
        """Performs connections with coord in neighborhood

        :param sample: a sample to perform connections with
        """
        # find near nodes to connect
        near_nodes = self._k_neighborhood(sample)

        self._add_edges([(sample, node) for node in near_nodes])

    def add_samples(self, num_samples: int) -> None:
        """Adds samples to roadmap

        :param num_samples: num to sample
        """
        samples = [self._environment.sample(is_safe_sample=False) for _ in range(num_samples)]

        # add nodes to graph
        self._add_points(samples)

        # add legal edges to graph
        for sample in samples:
            self._perform_connections(sample)
