from typing import Tuple

import numpy as np

from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path

EPSILON = 1
INF = 1000


def two_threats_shortest_path(source: Coord, target: Coord, circle1: Circle, circle2: Circle) \
        -> Tuple[Path, float, float]:
    path = Path([source, target])

    circles_intersection_length = sum(
        [circle.path_intersection_length(path) for circle in [circle1, circle2]]
    )
    return path, path.length, circles_intersection_length


def _considering_both_circles_blackbox_method(source: Coord, target: Coord, circle1: Circle, circle2: Circle,
                                              budget: float,
                                              alpha: float = 0.5
                                              ) -> Tuple[Path, float, float]:
    b1, b2 = alpha * budget, (1 - alpha) * budget

    partition = Circle.calculate_partition_between_circles(circle1, circle2, source, target, [circle1, circle2])

    def L(d: float) -> Path:
        mid_target = partition.start.shifted(d, partition.angle)
        return Path.concat_paths(
            single_threat_shortest_path_with_budget_constraint(source, mid_target, circle1, b1)[0],
            single_threat_shortest_path_with_budget_constraint(mid_target, target, circle2, b2)[0]
        )

    path = min([L(d) for d in np.arange(0, partition.length, 1)], key=lambda p: p.length)

    return path, path.length, circle1.path_intersection_length(path) + circle2.path_intersection_length(path)


def two_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float
) -> Tuple[Path, float, float]:
    direct_result = two_threats_shortest_path(source, target, circle1, circle2)
    if direct_result[2] <= budget:
        return direct_result

    circle1, circle2 = min([(circle1, circle2), (circle2, circle1)],
                           key=lambda c1c2: c1c2[0].distance_to(source) + c1c2[1].distance_to(target))

    path, length, risk = min([_considering_both_circles_blackbox_method(source, target, circle1, circle2, budget, alpha)
                              for alpha in np.arange(0, 1.01, 0.1)], key=lambda plr: plr[1])
    return path, length, risk


import matplotlib.pyplot as plt

if __name__ == '__main__':
    c1 = Circle(Coord(200, 100), 100)
    c2 = Circle(Coord(400, 125), 75)
    source = Coord(0, 0)
    target = Coord(500, 200)
    budget = 200
    path, length, risk = two_threats_shortest_path_with_budget_constraint(
        source, target, c1, c2, budget)
    title = f'length {round(length, 2)} risk {round(risk, 2)}'
    plt.title(title)
    plt.gca().set_aspect('equal', adjustable='box')
    path.plot()
    source.plot()
    target.plot()
    c1.plot()
    c2.plot()
    plt.show()
