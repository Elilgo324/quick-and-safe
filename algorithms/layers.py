from typing import List, Tuple

from environment.environment import Environment
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from roadmaps.rrg import RRG


def layers_multiple_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circles: List[Circle], budget: float) -> Tuple[Path, float, float]:
    print('running layers algorithm')
    environment = Environment(source, target, circles)
    rrg = RRG(environment)
    rrg.add_samples(2000)

    return rrg.constrained_shortest_path(budget=budget)
