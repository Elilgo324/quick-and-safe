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
from geometry.geometric import calculate_outer_tangent_points_of_circles, calculate_inner_tangent_points_of_circles
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


def _both_walking_on_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    s_contact, t_contact = _two_threats_compute_s_t_contact_points(source, target, circle1, circle2)

    exit_point1 = circle1.calculate_exit_point(s_contact, b1, t_contact)
    exit_point2 = circle2.calculate_exit_point(t_contact, b2, s_contact)

    c1_upper, c1_lower, c2_upper, c2_lower = calculate_outer_tangent_points_of_circles(
        circle1.center, circle1.radius, circle2.center, circle2.radius)
    t1_upper, t1_lower, t2_upper, t2_lower = calculate_inner_tangent_points_of_circles(
        circle1.center, circle1.radius, circle2.center, circle2.radius)

    contact1, contact2 = min([(c1_upper, c2_upper), (c1_lower, c2_lower), (t1_upper, t2_lower), (t1_lower, t2_upper)],
                             key=lambda xy: xy[0].distance_to(source) + xy[1].distance_to(target) + xy[0].distance_to(
                                 xy[1]))

    path = Path(
        [source, s_contact, exit_point1] + circle1.get_boundary_between(exit_point1, contact1)
        + [contact1, contact2] + circle2.get_boundary_between(contact2, exit_point2) + [exit_point2, t_contact, target]
    )
    return path, path.length, b1 + b2


def _first_walking_on_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> Tuple[float, Path]:
        p1_i = center1.shifted(radius1, theta1)
        p1_o = circle1.calculate_exit_point(p1_i, b1, target)

        second_circle_path = single_threat_shortest_path_with_budget_constraint(p1_o, target, circle2, b2)

        return source.distance_to(p1_i) + second_circle_path[1], second_circle_path[0]

    theta1 = min(np.arange(0, 2 * math.pi, 0.05), key=lambda theta: L(theta)[0])

    pi1 = circle1.center.shifted(circle1.radius, theta1)
    po1 = circle1.calculate_exit_point(pi1, b1, target)

    path = Path.concat_paths(Path([source, pi1, po1]), L(theta1)[1])

    return path, path.length, \
           circle1.path_intersection(path) + circle2.path_intersection(path)


def _second_walking_on_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    path, length, risk = _first_walking_on_chord(target, source, circle2, circle1, b2, b1)
    return Path(path.coords[::-1]), length, risk


def _considering_only_first_circle(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    path, length, risk = single_threat_shortest_path_with_budget_constraint(target, source, circle1, budget)
    return path, length, risk + circle2.path_intersection(path)

def two_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float, alpha: float = 0.5
) -> Tuple[Path, float, float]:
    circle1, circle2 = min([(circle1, circle2), (circle2, circle1)],
                           key=lambda c1c2: c1c2[0].distance_to(source) + c1c2[1].distance_to(target))

    direct_result = two_threats_shortest_path(source, target, circle1, circle2)

    only_first_result = _considering_only_first_circle(source, target, circle1, circle2, budget)

    only_second_result = _considering_only_first_circle(source, target, circle2, circle1, budget)

    b1, b2 = alpha * budget, (1 - alpha) * budget
    both_arc_result = _both_walking_on_arc(source, target, circle1, circle2, b1, b2)

    first_chord_result = _first_walking_on_chord(source, target, circle1, circle2, b1, b2)

    second_chord_result = _second_walking_on_chord(source, target, circle1, circle2, b1, b2)

    legal_results = [result for result in [
        direct_result, only_first_result, only_second_result, both_arc_result, first_chord_result, second_chord_result]
                     if result[2] <= budget]

    return min(legal_results, key=lambda r: r[1])


if __name__ == '__main__':
    source = Coord(0, 200)
    target = Coord(700, 0)
    c1 = Circle(Coord(200, 100), 100)
    c2 = Circle(Coord(500, 100), 100)
    path, length, risk = two_threats_shortest_path_with_budget_constraint(source, target, c1, c2, 5)
    plt.title(f'length {round(length, 2)} risk {round(risk, 2)}')
    plt.gca().set_aspect('equal', adjustable='box')
    path.plot()
    c1.plot()
    c2.plot()
    plt.show()

# def two_threats_shortest_path_with_budget_constraint(
#         source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float, alpha: float = 0.5
# ) -> Tuple[Path, float, float]:
#     circle1, circle2 = min([(circle1, circle2), (circle2, circle1)],
#                            key=lambda c1c2: c1c2[0].distance_to(source) + c1c2[1].distance_to(target))
#
#     # direct_result = two_threats_shortest_path(source, target, circle1, circle2)
#     #
#     # only_first_result = _considering_only_first_circle(source, target, circle1, circle2, budget)
#     #
#     # only_second_result = _considering_only_first_circle(source, target, circle2, circle1, budget)
#
#     plt.figure(figsize=(10,10))
#     plt.subplot(4,1,1)
#     plt.gca().set_aspect('equal', adjustable='box')
#     circle1.plot()
#     circle2.plot()
#
#     l1 = []
#     l2 = []
#     l3 = []
#
#     r1 = []
#     r2 = []
#     r3 = []
#
#     alphas = arange(0,0.51,0.1)
#     for alpha in tqdm(alphas):
#         b1, b2 = alpha * budget, (1 - alpha) * budget
#         both_arc_result = _both_walking_on_arc(source, target, circle1, circle2, b1, b2)
#         l1.append(both_arc_result[1])
#         r1.append(both_arc_result[2])
#
#         first_chord_result = _first_walking_on_chord(source, target, circle1, circle2, b1, b2)
#         l2.append(first_chord_result[1])
#         r2.append(first_chord_result[2])
#
#         second_chord_result = _second_walking_on_chord(source, target, circle1, circle2, b1, b2)
#         l3.append(second_chord_result[1])
#         r3.append(second_chord_result[2])
#
#     plt.subplot(4, 1, 2)
#     plt.plot(alphas, l1, color='blue')
#     plt.plot(alphas, r1, color='red')
#
#     plt.subplot(4, 1, 3)
#     plt.plot(alphas, l2, color='blue')
#     plt.plot(alphas, r2, color='red')
#
#     plt.subplot(4, 1, 4)
#     plt.plot(alphas, l3, color='blue')
#     plt.plot(alphas, r3, color='red')
#
#     plt.show()
#
#         # legal_results = [result for result in [
#         #     direct_result, only_first_result, only_second_result, both_arc_result, first_chord_result, second_chord_result]
#         #                  if result[2] <= budget]
#
#     # return min(legal_results, key=lambda r: r[1])
#
#
# if __name__ == '__main__':
#     source = Coord(0, 200)
#     target = Coord(700, 50)
#     c1 = Circle(Coord(200, 100), 100)
#     c2 = Circle(Coord(500, 100), 100)
#     two_threats_shortest_path_with_budget_constraint(source, target, c1, c2, 200)
#     # plt.title(f'length {round(length, 2)} risk {round(risk, 2)}')
#     # plt.gca().set_aspect('equal', adjustable='box')
#     # path.plot()
#     # c1.plot()
#     # c2.plot()
#     # plt.show()

# if __name__ == '__main__':
#     target = Coord(400, -100)
#     source = Coord(-50, 300)
#     c1 = Circle(Coord(100, 50), 100)
#     c2 = Circle(Coord(400, 50), 100)
#     c3 = c1
#
#     c1 = c2
#     c2 = c3
#
#     ts = calculate_inner_tangent_points_of_circles(c1.center, c1.radius, c2.center, c2.radius)
#
#     for t in ts:
#         t.plot()
#
#     c1.plot()
#     c2.plot()
#
#
#     plt.show()
