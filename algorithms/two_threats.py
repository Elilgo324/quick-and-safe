import math
from itertools import product
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point

from algorithms.multiple_threats import multiple_threats_shortest_path
from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.geometric import calculate_tangent_points_of_circles
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


def _consider_one_circle(source: Coord, target: Coord, considered_circle: Circle, neglected_circle: Circle,
                         budget: float) -> Tuple[Path, float, float]:
    path, length, risk = single_threat_shortest_path_with_budget_constraint(source, target, considered_circle, budget)
    return path, length, risk + neglected_circle.path_intersection(path)


def _both_walking_on_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    s_contact, t_contact = _two_threats_compute_s_t_contact_points(source, target, circle1, circle2)

    exit_point1 = circle1.calculate_exit_point(s_contact, b1, t_contact)
    exit_point2 = circle2.calculate_exit_point(t_contact, b2, s_contact)

    c1_upper, c1_lower, c2_upper, c2_lower = calculate_tangent_points_of_circles(
        circle1.center, circle1.radius, circle2.center, circle2.radius)
    contact1, contact2 = min([(c1_upper, c2_upper), (c1_lower, c2_lower)],
                             key=lambda xy: xy[0].distance_to(source) + xy[1].distance_to(target)
                             )

    path = Path(
        [source, s_contact, exit_point1] + circle1.get_boundary_between(exit_point1, contact1)
        + [contact1, contact2] + circle2.get_boundary_between(contact2, exit_point2) + [exit_point2, t_contact, target]
    )
    return path, path.length, b1 + b2


def _both_walking_on_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> float:
        p1_i = center1.shifted(radius1, theta1)
        p1_o = circle1.calculate_exit_point(p1_i, b1, target)

        return source.distance_to(p1_i) \
               + single_threat_shortest_path_with_budget_constraint(p1_o, target, circle2, b2)[1]

    theta1 = min(zip(np.arange(0, 2 * math.pi, 0.05), key=L)
    theta2 = 0

    pi1 = circle1.center.shifted(circle1.radius, theta1)
    po1 = circle1.calculate_exit_point(pi1, b1, target)
    pi2 = circle2.center.shifted(circle2.radius, theta2)
    po2 = circle2.calculate_exit_point(pi2, b2, target)

    path = Path([source, pi1, po1, pi2, po2, target])
    return path, path.length, b1 + b2


def _walking_on_chord_and_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    return _both_walking_on_chord(source, target, circle1, circle2, b1, b2)


def _walking_on_arc_and_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    path, length, risk = _both_walking_on_chord(target, source, circle2, circle1, b2, b1)
    return Path(path.coords[::-1]), length, risk


def two_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float, alpha: float = 0.5
) -> Tuple[Path, float, float]:
    direct_result = two_threats_shortest_path(source, target, circle1, circle2)
    only_first_result = _consider_one_circle(source, target, circle1, circle2, budget)
    only_second_result = _consider_one_circle(source, target, circle2, circle1, budget)

    b1, b2 = alpha * budget, (1 - alpha) * budget
    both_arc_result = _both_walking_on_arc(source, target, circle1, circle2, b1, b2)

    both_chord_result = _both_walking_on_chord(source, target, circle1, circle2, b1, b2)

    arc_chord_result = _walking_on_chord_and_arc(source, target, circle1, circle2, b1, b2)

    chord_arc_result = _walking_on_arc_and_chord(source, target, circle1, circle2, b1, b2)

    legal_results = [result for result in [
        direct_result, only_first_result, only_second_result, both_arc_result,
        both_chord_result, arc_chord_result, chord_arc_result] if result[2] <= budget]

    # legal_results = [result for result in [
    #     direct_result, only_first_result, only_second_result, both_arc_result] if result[2] <= budget]

    return min(legal_results, key=lambda r: r[1])


if __name__ == '__main__':
    source = Coord(0, 0)
    target = Coord(500, 0)
    c1 = Circle(Coord(100, 50), 100)
    c2 = Circle(Coord(300, 50), 100)
    path, length, risk = _both_walking_on_chord(source, target, c1, c2, 180, 180)
    print(f'length {length} risk {risk}')
    path.plot()
    c1.plot()
    c2.plot()
    plt.show()
