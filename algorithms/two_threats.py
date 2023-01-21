import math
from typing import Tuple

from shapely import Point

from algorithms.multiple_threats import multiple_threats_shortest_path
from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from geometry.segment import Segment


def two_threats_shortest_path(source: Coord, target: Coord, circle1: Circle, circle2: Circle) \
        -> Tuple[Path, float, float]:
    return multiple_threats_shortest_path(source, target, [circle1, circle2])


EPSILON = 5


def two_threats_shortest_path_with_budget_constraint_discretized_mid_targets(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, risk_limit: float, budgets: Tuple[float, float]
) -> Tuple[Path, float, float]:
    # find one mid-target
    circles_centers_segment = Segment(circle1.center, circle2.center)
    first_mid_target = circle1.center.shifted(distance=circle1.radius + EPSILON, angle=circles_centers_segment.angle)
    halfspace_angle = circles_centers_segment.angle + 0.5 * math.pi

    # find all mid-targets
    convex_hull = circle1.polygon.union(circle2.polygon).convex_hull

    mid_targets = []
    i = EPSILON
    while True:
        shifted = first_mid_target.shifted(distance=i, angle=halfspace_angle)
        if not convex_hull.contains(Point(shifted.xy)):
            break
        mid_targets.append(shifted)
        i += EPSILON

    i = EPSILON
    while True:
        shifted = first_mid_target.shifted(distance=i, angle=halfspace_angle + math.pi)
        if not convex_hull.contains(Point(shifted.xy)):
            break
        mid_targets.append(shifted)
        i += EPSILON

    # calculate path for each mid-target
    optional_paths = {mid_target: None for mid_target in mid_targets}

    for mid_target in mid_targets:
        path_to, length_to, risk_to = single_threat_shortest_path_with_budget_constraint(
            source, mid_target, circle1, risk_limit * budgets[0])
        path_from, length_from, risk_from = single_threat_shortest_path_with_budget_constraint(
            mid_target, target, circle2, risk_limit * budgets[1])
        optional_paths[mid_target] = {'path': path_to + path_from,
                                      'length': length_to + length_from,
                                      'risk': risk_to + risk_from}

    min_mid_target = min(mid_targets, key=lambda t: optional_paths[t]['length'])

    return optional_paths[min_mid_target]['path'], \
           optional_paths[min_mid_target]['length'], \
           optional_paths[min_mid_target]['risk']
