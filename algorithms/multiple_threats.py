from typing import List, Tuple

from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path


def multiple_threats_shortest_path(source: Coord, target: Coord, circles: List[Circle]) -> Tuple[Path, float, float]:
    path = Path([source, target])

    threat_intersection_length = sum(
        [path.to_shapely.intersection(circle.inner_polygon).length for circle in circles]
    )

    return path, path.length, threat_intersection_length


MID_TARGET_STEP = 5


def multiple_threats_shortest_path_with_budget_constraint_discretized_mid_targets(
        source: Coord, target: Coord, circles: List[Circle], budget: float, budgets: Tuple[float, float]
) -> Tuple[Path, float, float]:
    # TBD do with bottleneck logic
    pass


def multiple_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, threats: List[Circle], risk_limit: float, budgets) -> Tuple[
    List[Coord], float, float, Tuple]:
    pass
