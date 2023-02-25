from copy import deepcopy
from itertools import combinations

from roadmap.roadmap import Roadmap

from environment.environment import Environment


class VisibilityRoadmap(Roadmap):
    def __init__(self, environment: Environment) -> None:
        """Init of visibility roadmaps

        :param environment: the environment
        """
        super().__init__(environment)

        potential_nodes = deepcopy(environment.endpoints)
        for threat in self._environment.circles:
            potential_nodes.extend(threat.boundary)

        edges = []
        for p1, p2 in combinations(potential_nodes, 2):
            # if environment.is_safe_edge(p1,p2):
            edges.append((p1, p2))

        self._add_edges(edges)
