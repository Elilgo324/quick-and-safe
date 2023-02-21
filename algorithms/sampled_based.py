from typing import Tuple, List

from environment.environment import Environment
from geometry.circle import Circle
from geometry.coord import Coord


def multiple_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, threats: List[Circle], risk_limit: float, budgets) -> Tuple[
    List[Coord], float, float, Tuple]:
    environment = Environment(source, target)
    pass
