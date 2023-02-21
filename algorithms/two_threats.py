import math
from itertools import product
from typing import Tuple

import numpy as np
from tqdm import tqdm

from algorithms.multiple_threats import multiple_threats_shortest_path
from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint, _walking_on_chord, \
    _walking_on_arc
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.geometric import calculate_outer_tangent_points_of_circles, calculate_inner_tangent_points_of_circles
from geometry.path import Path
from geometry.segment import Segment

EPSILON = 1


def two_threats_shortest_path(source: Coord, target: Coord, circle1: Circle, circle2: Circle) \
        -> Tuple[Path, float, float]:
    return multiple_threats_shortest_path(source, target, [circle1, circle2])


def _considering_only_first_circle(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    path, length, risk = single_threat_shortest_path_with_budget_constraint(target, source, circle1, budget)
    return path, length, risk + circle2.path_intersection(path)


# cases method

def _two_threats_compute_s_t_contact_points(source: Coord, target: Coord, circle1: Circle, circle2: Circle) \
        -> Tuple[Coord, Coord]:
    s_contact1, s_contact2 = source.contact_points_with_circle(circle1.center, circle1.radius)
    t_contact1, t_contact2 = target.contact_points_with_circle(circle2.center, circle2.radius)

    return min(product([s_contact1, s_contact2], [t_contact1, t_contact2]),
               key=lambda p1p2: Path([source, p1p2[0], p1p2[1], target]).length)


def _both_walking_on_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> Tuple[float, Path]:
        p1_i = center1.shifted(radius1, theta1)
        p1_o = circle1.calculate_exit_point(p1_i, b1, target)

        second_circle_path = _walking_on_chord(p1_o, target, circle2, b2, True)

        return source.distance_to(p1_i) + second_circle_path[1], second_circle_path[0]

    theta1 = min(np.arange(0, 2 * math.pi, 0.05), key=lambda theta: L(theta)[0])

    pi1 = circle1.center.shifted(circle1.radius, theta1)
    po1 = circle1.calculate_exit_point(pi1, b1, target)

    path = Path.concat_paths(Path([source, pi1, po1]), L(theta1)[1])

    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def _both_walking_on_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    s_contact, t_contact = _two_threats_compute_s_t_contact_points(source, target, circle1, circle2)

    exit_point1 = circle1.calculate_exit_point(s_contact, b1, t_contact)
    exit_point2 = circle2.calculate_exit_point(t_contact, b2, s_contact)

    c1_upper, c1_lower, c2_upper, c2_lower = calculate_outer_tangent_points_of_circles(
        circle1.center, circle1.radius, circle2.center, circle2.radius)

    t1_upper, t1_lower, t2_upper, t2_lower = calculate_inner_tangent_points_of_circles(
        circle1.center, circle1.radius, circle2.center, circle2.radius)

    contact1, contact2 = min(
        [(c1_upper, c2_upper), (c1_lower, c2_lower), (t1_upper, t2_lower), (t1_lower, t2_upper)],
        key=lambda xy: xy[0].distance_to(source) + xy[1].distance_to(target) + xy[0].distance_to(xy[1]))

    subpath1 = [source, s_contact]
    if s_contact.distance_to(contact1) > b1:
        subpath1 += [exit_point1] + circle1.get_boundary_between(exit_point1, contact1)
    subpath1 += [contact1]

    subpath2 = [contact2]
    if t_contact.distance_to(contact2) > b2:
        subpath2 += circle2.get_boundary_between(contact2, exit_point2) + [exit_point2]
    subpath2 += [t_contact, target]

    path = Path(subpath1 + subpath2)
    return path, path.length, b1 + b2


def _first_st_second_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> Tuple[float, Path]:
        p1_o = center1.shifted(radius1, theta1)
        b1 = circle1.path_intersection(Path([source, center1.shifted(radius1, theta1)]))

        try:
            second_circle_path = _walking_on_chord(p1_o, target, circle2, budget - b1)
        except:
            return 10_000, Path([])

        return source.distance_to(p1_o) + second_circle_path[1], second_circle_path[0]

    # TBD enforce range to be valid
    theta1 = min(np.arange(0, 2 * math.pi, 0.05), key=lambda theta: L(theta)[0])

    po1 = center1.shifted(radius1, theta1)

    path = Path.concat_paths(Path([source, po1]), L(theta1)[1])

    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def _first_arc_second_st(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    reversed_result = _first_st_second_arc(target, source, circle2, circle1, budget)
    return Path(reversed_result[0].coords[::-1]), reversed_result[1], reversed_result[2]


def _first_st_second_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> Tuple[float, Path]:
        p1_o = center1.shifted(radius1, theta1)
        b1 = circle1.path_intersection(Path([source, center1.shifted(radius1, theta1)]))

        try:
            second_circle_path = _walking_on_arc(p1_o, target, circle2, budget - b1)
        except:
            return 10_000, Path([])

        return source.distance_to(p1_o) + second_circle_path[1], second_circle_path[0]

    # TBD enforce range to be valid
    theta1 = min(np.arange(0, 2 * math.pi, 0.05), key=lambda theta: L(theta)[0])

    po1 = center1.shifted(radius1, theta1)

    path = Path.concat_paths(Path([source, po1]), L(theta1)[1])

    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def _first_chord_second_st(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    reversed_result = _first_st_second_chord(target, source, circle2, circle1, budget)
    return Path(reversed_result[0].coords[::-1]), reversed_result[1], reversed_result[2]


def _first_chord_second_arc(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> Tuple[float, Path]:
        p1_i = center1.shifted(radius1, theta1)
        p1_o = circle1.calculate_exit_point(p1_i, b1, target)

        second_circle_path = _walking_on_arc(p1_o, target, circle2, b2, True)

        return source.distance_to(p1_i) + second_circle_path[1], second_circle_path[0]

    theta1 = min(np.arange(0, 2 * math.pi, 0.05), key=lambda theta: L(theta)[0])

    pi1 = circle1.center.shifted(circle1.radius, theta1)
    po1 = circle1.calculate_exit_point(pi1, b1, target)

    path = Path.concat_paths(Path([source, pi1, po1]), L(theta1)[1])

    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def _first_arc_second_chord(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    reversed_result = _first_chord_second_arc(target, source, circle2, circle1, b2, b1)
    return Path(reversed_result[0].coords[::-1]), reversed_result[1], reversed_result[2]


def two_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float, alpha: float = 0.5
) -> Tuple[Path, float, float]:
    circle1, circle2 = min([(circle1, circle2), (circle2, circle1)],
                           key=lambda c1c2: c1c2[0].distance_to(source) + c1c2[1].distance_to(target))

    both_st_result = two_threats_shortest_path(source, target, circle1, circle2)
    if both_st_result[2] <= budget:
        return both_st_result

    only_first_result = _considering_only_first_circle(source, target, circle1, circle2, budget)

    only_second_result = _considering_only_first_circle(source, target, circle2, circle1, budget)

    st_chord_result = _first_st_second_chord(source, target, circle1, circle2, budget)

    chord_st_result = _first_chord_second_st(source, target, circle1, circle2, budget)

    st_arc_result = _first_st_second_chord(source, target, circle1, circle2, budget)

    arc_st_result = _first_chord_second_st(source, target, circle1, circle2, budget)

    b1, b2 = alpha * budget, (1 - alpha) * budget

    chord_chord_result = _both_walking_on_chord(source, target, circle1, circle2, b1, b2)

    arc_arc_result = _both_walking_on_arc(source, target, circle1, circle2, b1, b2)

    chord_arc_result = _first_chord_second_arc(source, target, circle1, circle2, b1, b2)

    arc_chord_result = _first_arc_second_chord(source, target, circle1, circle2, b1, b2)

    legal_results = [chord_chord_result, arc_arc_result, st_chord_result, chord_st_result, st_arc_result, arc_st_result,
                     chord_arc_result, arc_chord_result]

    legal_results += [result for result in [only_first_result, only_second_result] if
                      result[2] <= budget]

    return min(legal_results, key=lambda r: r[1])


# blackbox method

def _considering_both_circles_blackbox_method(source: Coord, target: Coord, circle1: Circle, circle2: Circle,
                                              budget: float,
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
            _walking_on_chord(source, mid_target, circle1, b1)[0],
            _walking_on_arc(mid_target, target, circle2, b2)[0]
        )

    d_star = None
    l_star = 10_000
    for d in np.arange(0, partition.length, 1):
        try:
            l = L(d).length
            if l < l_star:
                l_star = l
                d_star = d
        except:
            pass

    if d_star is None:
        raise Exception(f'no d star found')

    path = L(d_star)
    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def two_threats_shortest_path_with_budget_constraint_blackbox_method(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float, alpha: float = 0.5
) -> Tuple[Path, float, float]:
    direct_result = two_threats_shortest_path(source, target, circle1, circle2)
    if direct_result[2] <= budget:
        return direct_result

    only_first_result = _considering_only_first_circle(source, target, circle1, circle2, budget)

    only_second_result = _considering_only_first_circle(source, target, circle2, circle1, budget)

    both_result = _considering_both_circles_blackbox_method(source, target, circle1, circle2, budget, alpha)

    legal_results = [both_result] + [result for result in [only_first_result, only_second_result] if
                                     result[2] <= budget]

    return min(legal_results, key=lambda r: r[1])


import matplotlib.pyplot as plt

if __name__ == '__main__':
    c1 = Circle(Coord(200, 100), 100)
    c2 = Circle(Coord(400, 125), 75)
    source = Coord(0, 125)
    target = Coord(500, 150)
    budget = 300
    # two_threats_shortest_path_with_budget_constraint_blackbox_method(
    #     source, target, c1, c2, budget, 0.2)
    plt.subplot(2, 1, 1)
    title = f'st-st length as function of alpha (budget={budget})'
    plt.title(title)
    plt.gca().set_aspect('equal', adjustable='box')
    # path.plot()
    source.plot()
    target.plot()
    c1.plot()
    c2.plot()

    plt.subplot(2, 1, 2)
    alphas = np.arange(0, 1.01, 0.025)
    als = []
    lengths = []
    for alpha in tqdm(alphas):
        try:
            path, length, _ = _considering_both_circles_blackbox_method(
                source, target, c1, c2, budget, alpha)
            als.append(alpha)
            lengths.append(length)
        except:
            pass
    plt.plot(als, lengths)

    # plt.show()
    plt.savefig(title + '.png')

# if __name__ == '__main__':
#     c1 = Circle(Coord(200, 100), 100)
#     c2 = Circle(Coord(400, 125), 70)
#     source = Coord(0, 125)
#     target = Coord(600, 50)
#     budget = 300
#     alpha = 0.75
#     # path, length, risk = two_threats_shortest_path_with_budget_constraint_blackbox_method(
#     #     source, target, c1, c2, budget, 0.5)
#     plt.subplot(2, 1, 1)
#     # plt.title(f'length {round(length, 2)} risk {round(risk, 2)}')
#     title = f'length as function of mid target shift (alpha={alpha} budget={budget})'
#     plt.title(title)
#     plt.gca().set_aspect('equal', adjustable='box')
#     # path.plot()
#     source.plot()
#     target.plot()
#     c1.plot()
#     c2.plot()
#
#     plt.subplot(2, 1, 2)
#
#     _considering_both_circles_blackbox_method(source, target, c1, c2, budget, alpha)
#
#     # plt.show()
#     plt.savefig(title + '.png')
