import math
from typing import Tuple

import numpy as np

from algorithms.multiple_threats import multiple_threats_shortest_path
from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.geometric import calculate_outer_tangent_angles_of_circles
from geometry.path import Path


def two_threats_shortest_path(source: Coord, target: Coord, circle1: Circle, circle2: Circle) \
        -> Tuple[Path, float, float]:
    return multiple_threats_shortest_path(source, target, [circle1, circle2])


MID_TARGET_STEP = 5


def _first_st_planning(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> Path:
        p1_o = center1.shifted(radius1, theta1)

        b2 = budget - circle1.path_intersection(Path([source, p1_o]))

        second_circle_path = single_threat_shortest_path_with_budget_constraint(p1_o, target, circle2, b2)

        return Path.concat_paths(Path([source, p1_o]), second_circle_path[0])

    upper_theta, lower_theta = calculate_outer_tangent_angles_of_circles(center1, radius1, center2, radius2)
    theta1 = min(np.arange(lower_theta, upper_theta, 0.1), key=lambda theta: L(theta).length)
    path = L(theta1)

    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def _first_circumference_planning(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> Path:
        p1_l = center1.shifted(radius1, theta1)
        p1_o = circle1.calculate_exit_point(p1_l, b1, source)

        s_contact1, s_contact2 = source.contact_points_with_circle(circle1.center, circle1.radius)
        s_contact = min([s_contact1, s_contact2], key=lambda sc: sc.distance_to(p1_o))

        second_circle_path = single_threat_shortest_path_with_budget_constraint(p1_l, target, circle2, b2)

        return Path.concat_paths(
            Path([source, s_contact, p1_o] + circle1.get_boundary_between(p1_o, p1_l)), second_circle_path[0])

    upper_theta, lower_theta = calculate_outer_tangent_angles_of_circles(center1, radius1, center2, radius2)
    theta1 = min(np.arange(lower_theta, upper_theta, 0.1), key=lambda theta: L(theta).length)
    path = L(theta1)

    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def _first_chord_planning(source: Coord, target: Coord, circle1: Circle, circle2: Circle, b1: float, b2: float) \
        -> Tuple[Path, float, float]:
    center1, center2 = circle1.center, circle2.center
    radius1, radius2 = circle1.radius, circle2.radius

    def L(theta1: float) -> Path:
        p1_i = center1.shifted(radius1, theta1)
        p1_o = circle1.calculate_exit_point(p1_i, b1, target)
        print(p1_o)

        second_circle_path = single_threat_shortest_path_with_budget_constraint(p1_o, target, circle2, b2)

        return Path.concat_paths(Path([source, p1_i, p1_o]), second_circle_path[0])

    upper_theta, lower_theta = calculate_outer_tangent_angles_of_circles(center1, radius1, center2, radius2)
    theta1 = min(np.arange(math.pi + lower_theta, math.pi + upper_theta, 0.1), key=lambda theta: L(theta).length)
    path = L(theta1)

    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def two_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float, alpha: float = 0.5
) -> Tuple[Path, float, float]:
    circle1, circle2 = min([(circle1, circle2), (circle2, circle1)],
                           key=lambda c1c2: c1c2[0].distance_to(source) + c1c2[1].distance_to(target))

    first_st_result = _first_st_planning(source, target, circle1, circle2, budget)

    b1, b2 = alpha * budget, (1 - alpha) * budget

    first_circumference_result = _first_circumference_planning(source, target, circle1, circle2, b1, b2)

    first_chord_result = _first_chord_planning(source, target, circle1, circle2, b1, b2)

    legal_results = [result for result in [first_st_result, first_circumference_result, first_chord_result]
                     if result[2] <= budget]
    return first_circumference_result
    # return min(legal_results, key=lambda r: r[1])


import matplotlib.pyplot as plt

if __name__ == '__main__':
    c1 = Circle(Coord(200, 100), 100)
    c2 = Circle(Coord(400, 110), 75)
    source = Coord(0, 170)
    target = Coord(500, 120)
    path, length, risk = two_threats_shortest_path_with_budget_constraint(source, target, c1, c2, 300)
    plt.title(f'length {round(length, 2)} risk {round(risk, 2)}')
    plt.gca().set_aspect('equal', adjustable='box')
    path.plot()
    c1.plot()
    c2.plot()
    plt.show()
