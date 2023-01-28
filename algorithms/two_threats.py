import math
from itertools import product
from typing import Tuple

import matplotlib.pyplot as plt
from shapely import Point

from algorithms.multiple_threats import multiple_threats_shortest_path
from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.geometric import calculate_points_in_distance_on_circle
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


def _two_threats_compute_s_t_contact_points(source: Coord, target: Coord, circle1: Circle, circle2: Circle) \
        -> Tuple[Coord, Coord]:
    s_contact1, s_contact2 = source.contact_points_with_circle(circle1.center, circle1.radius)
    t_contact1, t_contact2 = target.contact_points_with_circle(circle2.center, circle2.radius)

    return min(product([s_contact1, s_contact2], [t_contact1, t_contact2]),
               key=lambda p1p2: Path([source, p1p2[0], p1p2[1], target]).length)


def _both_walking_on_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    s_contact, t_contact = _two_threats_compute_s_t_contact_points(source, target, circle1, circle2)

    ep1, ep2 = calculate_points_in_distance_on_circle(circle1.center, circle1.radius, s_contact, budget)
    exit_point1 = min([ep1, ep2], key=lambda p: p.distance_to(t_contact))

    ep1, ep2 = calculate_points_in_distance_on_circle(circle2.center, circle2.radius, t_contact, budget)
    exit_point2 = min([ep1, ep2], key=lambda p: p.distance_to(s_contact))

    path = Path([source, s_contact] + circle1.get_boundary_between(s_contact, exit_point1) + [exit_point1,
                                                                                              exit_point2] + circle2.get_boundary_between(
        exit_point2, t_contact) + [t_contact, target])
    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


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
    direct_result = two_threats_shortest_path(source, target, circle1, circle2)
    only_first_result = single_threat_shortest_path_with_budget_constraint(source, target, circle1, budget)
    only_second_result = single_threat_shortest_path_with_budget_constraint(source, target, circle2, budget)
    both_arc_result = _both_walking_on_arc(source, target, circle1, circle2, budget)
    both_chord_result = _both_walking_on_chord(source, target, circle1, circle2, budget)
    arc_chord_result = _walking_on_chord_and_arc(source, target, circle1, circle2, budget)
    chord_arc_result = _walking_on_arc_and_chord(source, target, circle1, circle2, budget)

    legal_results = [result for result in [
        direct_result, only_first_result, only_second_result, both_arc_result,
        both_chord_result, arc_chord_result, chord_arc_result] if result[2] <= budget]
    return min(legal_results, key=lambda r: r[1])


if __name__ == '__main__':
    source = Coord(0, 0)
    target = Coord(500, 0)
    c1 = Circle(Coord(100, 50), 100)
    c2 = Circle(Coord(300, 50), 100)
    path, length, risk = _both_walking_on_arc(source, target, c1, c2, 1)
    path.plot()
    c1.plot()
    c2.plot()
    plt.show()
