from copy import deepcopy

from settings.environment import Environment
from roadmap.roadmap import Roadmap
from itertools import combinations


class VisibilityRoadmap(Roadmap):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        potential_nodes = deepcopy(environment.endpoints)
        for threat in self._environment.threats:
            potential_nodes.extend(threat.get_buffered_boundary(1))

        edges = []
        for p1, p2 in combinations(potential_nodes, 2):
            # if environment.is_safe_edge(p1,p2):
            edges.append((p1, p2))

        self._add_edges(edges)
