import math
from typing import Tuple

import numpy as np

from algorithms.multiple_threats import multiple_threats_shortest_path
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.geometric import calculate_points_in_distance_on_circle, \
    calculate_angle_on_chord, calculate_directional_angle_of_line
from geometry.path import Path


def single_threat_shortest_path(source: Coord, target: Coord, circle: Circle) -> Tuple[Path, float, float]:
    return multiple_threats_shortest_path(source, target, [circle])


def _compute_s_t_contact_points(source: Coord, target: Coord, circle: Circle) -> Tuple[Coord, Coord]:
    corner = Coord(source.x, target.y)
    return min(source.contact_points_with_circle(circle.center, circle.radius),
               key=lambda p: (p.distance_to(target), p.distance_to(corner))), \
           min(target.contact_points_with_circle(circle.center, circle.radius),
               key=lambda p: (p.distance_to(source), p.distance_to(corner)))


def single_threat_safest_path(source: Coord, target: Coord, circle: Circle) -> Tuple[Path, float, float]:
    return _walking_on_arc(source, target, circle, budget=0)


def _walking_on_arc(source: Coord, target: Coord, circle: Circle, budget: float) -> Tuple[Path, float, float]:
    s_contact, t_contact = _compute_s_t_contact_points(source, target, circle)

    ep1, ep2 = calculate_points_in_distance_on_circle(circle.center, circle.radius, s_contact, budget)
    exit_point = min([ep1, ep2], key=lambda p: p.distance_to(t_contact))

    path = Path([source, s_contact] + circle.get_boundary_between(exit_point, t_contact) + [target])
    return path, path.length, budget


def _walking_on_chord(source: Coord, target: Coord, circle: Circle, budget: float) -> Tuple[Path, float, float]:
    s_contact, t_contact = _compute_s_t_contact_points(source, target, circle)
    center = circle.center
    radius = circle.radius

    # beta is the central angle supported by the chord
    beta = calculate_angle_on_chord(budget, radius)

    # two length functions of chords (+-beta) by a given parameter theta
    def L1(theta: float) -> float:
        entry_point = center.shifted(distance=radius, angle=theta)
        exit_point = center.shifted(distance=radius, angle=theta + beta)
        return source.distance_to(entry_point) + budget + target.distance_to(exit_point)

    def L2(theta: float) -> float:
        entry_point = center.shifted(distance=radius, angle=theta)
        exit_point = center.shifted(distance=radius, angle=theta - beta)
        return source.distance_to(entry_point) + budget + target.distance_to(exit_point)

    chord_start_of_t_contact = circle.calculate_exit_point(t_contact, budget, source)

    L_range = (calculate_directional_angle_of_line(start=center, end=s_contact),
               calculate_directional_angle_of_line(start=center, end=chord_start_of_t_contact))
    L_range = L_range if L_range[0] < L_range[1] else (L_range[1], L_range[0])

    # if passing through x-axis
    if L_range[0] + math.pi < L_range[1]:
        L_range = (L_range[1], L_range[0] + 2 * math.pi)

    theta1 = min(np.arange(L_range[0], L_range[1], 0.01), key=lambda theta: L1(theta))
    theta2 = min(np.arange(L_range[0], L_range[1], 0.01), key=lambda theta: L2(theta))

    theta = theta1
    exit_point_angle = theta + beta

    if L1(theta1) > L2(theta2):
        theta = theta2
        exit_point_angle = theta - beta

    entry_point = center.shifted(distance=radius, angle=theta)
    exit_point = center.shifted(distance=radius, angle=exit_point_angle)

    path = Path([source, entry_point, exit_point, target])

    return path, path.length, circle.path_intersection(path)


def single_threat_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle: Circle, budget: float
) -> Tuple[Path, float, float]:
    direct_result = single_threat_shortest_path(source, target, circle)
    arc_result = _walking_on_arc(source, target, circle, budget)
    chord_result = _walking_on_chord(source, target, circle, budget)

    legal_results = [result for result in [direct_result, arc_result, chord_result] if result[2] <= budget]
    return min(legal_results, key=lambda r: r[1])
