import math
from typing import Tuple, List

import numpy as np

from geometry.geometric import calculate_points_in_distance_on_circle, \
    calculate_arc_length_on_chord, calculate_angle_on_chord, calculate_directional_angle_of_line
from algorithms.multiple_threats import multiple_threats_shortest_path
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path


def single_threat_shortest_path(source: Coord, target: Coord, circle: Circle) -> Tuple[Path, float, float]:
    return multiple_threats_shortest_path(source, target, [circle])


def _compute_s_t_contact_points(source: Coord, target: Coord, circle: Circle) -> Tuple[Coord, Coord]:
    return min(source.contact_points_with_circle(circle.center, circle.radius), key=lambda p: p.distance_to(target)), \
           min(target.contact_points_with_circle(circle.center, circle.radius), key=lambda p: p.distance_to(source))


def single_threat_safest_path(source: Coord, target: Coord, circle: Circle) -> Tuple[Path, float, float]:
    source_contact, target_contact = _compute_s_t_contact_points(source, target, circle)
    path = Path([source] + circle.get_boundary_between(source_contact, target_contact) + [target])
    return path, path.length, 0


def _direct_connection(source: Coord, target: Coord, circle: Circle) -> Tuple[Path, float, float]:
    return single_threat_shortest_path(source, target, circle)


def _walking_on_arc(source: Coord, target: Coord, circle: Circle, budget: float) -> Tuple[Path, float, float]:
    s_contact, t_contact = _compute_s_t_contact_points(source, target, circle)

    ep1, ep2 = calculate_points_in_distance_on_circle(circle.center, circle.radius, s_contact, budget)
    exit_point = min([ep1, ep2], key=lambda p: p.distance_to(t_contact))

    path = Path([source, s_contact] + circle.get_boundary_between(exit_point, t_contact) + [target])
    return path, path.length, budget


def _walking_on_chord(source: Coord, target: Coord, circle: Circle, risk_limit: float) -> Tuple[
    List[Coord], float, float]:
    contact_distance = s_contact.distance_to(t_contact)
    center = circle.center
    radius = circle.radius

    # check case 3
    if contact_distance >= risk_limit:
        print(f'case 3: the risk limit {risk_limit} is under the contact points distance {round(contact_distance, 2)}')

        p1, p2 = calculate_points_in_distance_on_circle(center, radius, s_contact, risk_limit)
        p = min([p1, p2], key=lambda p: p.distance_to(t_contact))

        path = [source, s_contact] + circle.get_boundary_between(p, t_contact) + [target]
        path_length = source.distance_to(s_contact) \
                      + s_contact.distance_to(p) \
                      + calculate_arc_length_on_chord(p.distance_to(t_contact), radius) \
                      + t_contact.distance_to(target)
        return path, path_length, risk_limit

    # solving case 2
    print(f'case 2: the risk limit {risk_limit} is over the contact points distance {round(contact_distance, 2)}')
    beta = calculate_angle_on_chord(risk_limit, radius)

    def L1(theta: float) -> float:
        entry_point = center.shifted(distance=radius, angle=theta)
        exit_point = center.shifted(distance=radius, angle=theta + beta)
        return source.distance_to(entry_point) + risk_limit + target.distance_to(exit_point)

    def L2(theta: float) -> float:
        entry_point = center.shifted(distance=radius, angle=theta)
        exit_point = center.shifted(distance=radius, angle=theta - beta)
        return source.distance_to(entry_point) + risk_limit + target.distance_to(exit_point)

    p1, p2 = calculate_points_in_distance_on_circle(center, radius, t_contact, risk_limit)
    chord_start_of_t_contact = min([p1, p2], key=lambda p: p.distance_to(source))

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

    path = [source, entry_point, exit_point, target]
    path_length = source.distance_to(entry_point) + risk_limit + exit_point.distance_to(target)

    return path, path_length, risk_limit


def single_threat_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle: Circle, risk_limit: float
) -> Tuple[List[Coord], float, float]:
    direct_result = _direct_connection(source, target, circle)
    arc_result = _walking_on_arc(source, target, circle, risk_limit)
    chord_result = _walking_on_chord(source, target, circle)

    legal_results = [result for result in [direct_result, arc_result, chord_result] if result[2] < risk_limit]
    return min(legal_results, key=lambda r: r[1])
