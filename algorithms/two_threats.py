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


MID_TARGET_STEP = 5


def two_threats_shortest_path_with_budget_constraint_discretized_mid_targets(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, risk_limit: float, budgets: Tuple[float, float]
) -> Tuple[Path, float, float]:
    # find one mid-target
    circles_centers_segment = Segment(circle1.center, circle2.center)
    first_mid_target = circle1.center.shifted(distance=circle1.radius + MID_TARGET_STEP,
                                              angle=circles_centers_segment.angle)
    halfspace_angle = circles_centers_segment.angle + 0.5 * math.pi

    # find all mid-targets
    convex_hull = circle1.inner_polygon.union(circle2.inner_polygon).convex_hull

    mid_targets = []
    i = MID_TARGET_STEP
    while True:
        shifted = first_mid_target.shifted(distance=i, angle=halfspace_angle)
        if not convex_hull.contains(Point(shifted.xy)):
            break
        mid_targets.append(shifted)
        i += MID_TARGET_STEP

    i = MID_TARGET_STEP
    while True:
        shifted = first_mid_target.shifted(distance=i, angle=halfspace_angle + math.pi)
        if not convex_hull.contains(Point(shifted.xy)):
            break
        mid_targets.append(shifted)
        i += MID_TARGET_STEP

    # calculate path for each mid-target
    optional_paths = {mid_target: None for mid_target in mid_targets}

    for mid_target in mid_targets:
        path_to, length_to, risk_to = single_threat_shortest_path_with_budget_constraint(
            source, mid_target, circle1, risk_limit * budgets[0])
        path_from, length_from, risk_from = single_threat_shortest_path_with_budget_constraint(
            mid_target, target, circle2, risk_limit * budgets[1])
        optional_paths[mid_target] = {'path': Path.concat_paths(path_to, path_from),
                                      'length': length_to + length_from,
                                      'risk': risk_to + risk_from}

    min_mid_target = min(mid_targets, key=lambda t: optional_paths[t]['length'])

    return optional_paths[min_mid_target]['path'], \
           optional_paths[min_mid_target]['length'], \
           optional_paths[min_mid_target]['risk']


def _direct_connection(source: Coord, target: Coord, circle1: Circle, circle2: Circle) -> Tuple[Path, float, float]:
    return two_threats_shortest_path(source, target, circle1, circle2)


def _both_walking_on_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    return two_threats_shortest_path(source, target, circle1, circle2)


def _both_walking_on_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    return two_threats_shortest_path(source, target, circle1, circle2)


def _walking_on_chord_and_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    return two_threats_shortest_path(source, target, circle1, circle2)


def _walking_on_arc_and_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    return two_threats_shortest_path(source, target, circle1, circle2)


def two_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float
) -> Tuple[Path, float, float]:
    direct_result = _direct_connection(source, target, circle1, circle2)
    both_arc_result = _both_walking_on_arc(source, target, circle1, circle2, budget)
    both_chord_result = _both_walking_on_chord(source, target, circle1, circle2, budget)
    arc_chord_result = _walking_on_chord_and_arc(source, target, circle1, circle2, budget)
    chord_arc_result = _walking_on_arc_and_chord(source, target, circle1, circle2, budget)

    legal_results = [result for result in [
        direct_result, both_arc_result, both_chord_result, arc_chord_result, chord_arc_result] if result[2] <= budget]
    return min(legal_results, key=lambda r: r[1])
