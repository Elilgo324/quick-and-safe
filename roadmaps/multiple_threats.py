from typing import Tuple, List

import networkx as nx

from environment.environment import Environment
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from roadmaps.rrg import RRG


def multiple_threats_shortest_path(source: Coord, target: Coord, circles: List[Circle], graph: nx.Graph = None) -> \
Tuple[Path, float, float]:
    if graph is None:
        environment = Environment(source, target, circles)
        rrg = RRG(environment)
        rrg.add_samples(10)
        graph = rrg.graph
    path = Path([source, target])

    threat_intersection_length = sum(
        [circle.path_intersection_length(path) for circle in circles]
    )

    return path, path.length, threat_intersection_length


if __name__ == '__main__':
    c1 = Circle(Coord(200, 100), 100)
    c2 = Circle(Coord(400, 125), 75)
    source = Coord(0, 0)
    target = Coord(500, 200)
    budget = 200
    path, length, risk = multiple_threats_shortest_path(
        source, target, [c1, c2])


def multiple_threats_shortest_path_with_budget_constraint_discretized_mid_targets(
        source: Coord, target: Coord, circles: List[Circle], budget: float, budgets: Tuple[float, float]
) -> Tuple[Path, float, float]:
    # TBD do with bottleneck logic
    pass


def multiple_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, threats: List[Circle], risk_limit: float, budgets) -> Tuple[
    List[Coord], float, float, Tuple]:
    pass
