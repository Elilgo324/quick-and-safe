import math
from typing import Tuple

import numpy as np

from algorithms.multiple_threats import multiple_threats_shortest_path
from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.geometric import calculate_outer_tangent_points_of_circles
from geometry.path import Path
from geometry.segment import Segment

EPSILON = 1


def two_threats_shortest_path(source: Coord, target: Coord, circle1: Circle, circle2: Circle) \
        -> Tuple[Path, float, float]:
    return multiple_threats_shortest_path(source, target, [circle1, circle2])


def _considering_both_circles(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float,
                              alpha: float = 0.5
                              ) -> Tuple[Path, float, float]:
    b1, b2 = alpha * budget, (1 - alpha) * budget

    circle1, circle2 = min([(circle1, circle2), (circle2, circle1)],
                           key=lambda c1c2: c1c2[0].distance_to(source) + c1c2[1].distance_to(target))
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    centers_segment = Segment(center1, center2)
    centers_distance = centers_segment.length
    centers_angle = centers_segment.angle

    point_between = center1.shifted((radius1 + (centers_distance - radius2)) / 2, centers_angle)
    partition = Segment(
        point_between.shifted(max(radius1, radius2) + EPSILON, centers_angle + 0.5 * math.pi),
        point_between.shifted(max(radius1, radius2) + EPSILON, centers_angle - 0.5 * math.pi)
    )

    cp1_upper, cp1_lower, cp2_upper, cp2_lower = calculate_outer_tangent_points_of_circles(center1, radius1, center2,
                                                                                           radius2)
    upper_tangent = Segment(cp1_upper, cp2_upper)
    lower_tangent = Segment(cp1_lower, cp2_lower)

    partition = (partition.to_shapely.intersection(upper_tangent.to_shapely),
                 partition.to_shapely.intersection(lower_tangent.to_shapely))
    partition = Segment(Coord(partition[0].x, partition[0].y), Coord(partition[1].x, partition[1].y))

    def L(d: float) -> Path:
        mid_target = partition.start.shifted(d, partition.angle)
        return Path.concat_paths(
            single_threat_shortest_path_with_budget_constraint(source, mid_target, circle1, b1)[0],
            single_threat_shortest_path_with_budget_constraint(mid_target, target, circle2, b2)[0]
        )

    d_star = min(np.arange(0, partition.length, 1), key=lambda d: L(d).length)
    path = L(d_star)
    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def _considering_only_first_circle(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    path, length, risk = single_threat_shortest_path_with_budget_constraint(target, source, circle1, budget)
    return path, length, risk + circle2.path_intersection(path)


def two_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float, alpha: float = 0.5
) -> Tuple[Path, float, float]:
    direct_result = two_threats_shortest_path(source, target, circle1, circle2)
    if direct_result[2] <= budget:
        return direct_result

    only_first_result = _considering_only_first_circle(source, target, circle1, circle2, budget)

    only_second_result = _considering_only_first_circle(source, target, circle2, circle1, budget)

    both_result = _considering_both_circles(source, target, circle2, circle1, budget, alpha)

    legal_results = [result for result in [only_first_result, only_second_result, both_result] if result[2] <= budget]

    return min(legal_results, key=lambda r: r[1])


import matplotlib.pyplot as plt

if __name__ == '__main__':
    c1 = Circle(Coord(200, 100), 100)
    c2 = Circle(Coord(440, 80), 75)
    source = Coord(0, 170)
    target = Coord(540, 40)
    path, length, risk = two_threats_shortest_path_with_budget_constraint(source, target, c1, c2, 342, 0.5)
    plt.title(f'length {round(length, 2)} risk {round(risk, 2)}')
    plt.gca().set_aspect('equal', adjustable='box')
    path.plot()
    c1.plot()
    c2.plot()
    plt.show()
