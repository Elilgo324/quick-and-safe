import itertools
from typing import Tuple, List
from itertools import product, combinations

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, Point
from scipy.optimize import minimize_scalar
import math
from settings.environment import Environment
from settings.threat import Threat
from algorithms.geometric import is_left_side_of_line, \
    calculate_angle_on_chord, calculate_non_directional_angle_of_line, calculate_directional_angle_of_line, \
    calculate_points_in_distance_on_circle
from settings.coord import Coord
from settings.threat import Threat


def compute_path_length(path: List[Coord]) -> float:
    """Computes path length

    :param path: the path
    :return: the length of the path
    """
    return sum([c1.distance(c2) for c1, c2 in zip(path[:-1], path[1:])])


def shortest_path_single_threat(source: Coord, target: Coord, threat: Threat) -> Tuple[List[Coord], float, float]:
    """Computes the shortest path with single threat in the environment

    :param source: the source of the path
    :param target: the target of the path
    :param threat: the single threat
    :return: the shortest path, its length and its risk
    """
    source_target_line = LineString([source, target])
    threat_intersection = LineString(source_target_line.intersection(threat.polygon))

    return [source, target], source_target_line.length, threat_intersection.length


def shortest_path_multiple_threats(source: Coord, target: Coord, threats: List[Threat]) -> Tuple[
    List[Coord], float, float]:
    """Computes the shortest path with multiple threats in the environment

    :param source: the source of the path
    :param target: the target of the path
    :param threats: the threats
    :return: the shortest path, its length and its risk
    """
    source_target_line = LineString([source, target])

    threat_intersection_length = LineString(source_target_line.intersection(threats[0].polygon)).length
    for threat in threats[1:]:
        threat_intersection_length += LineString(source_target_line.intersection(threat.polygon)).length

    return [source, target], source_target_line.length, threat_intersection_length


def safest_path_single_threat(source: Coord, target: Coord, threat: Threat) -> Tuple[List[Coord], float, float]:
    """Computes the safest path with single threat in the environment

    :param source: the source of the path
    :param target: the target of the path
    :param threat: the single threat
    :return: the safest path, its length and its risk
    """
    # the 4 contact points of the source and the target
    source_contact1, source_contact2 = source.contact_points_with_circle(threat.center, threat.radius)
    target_contact1, target_contact2 = target.contact_points_with_circle(threat.center, threat.radius)

    # possible path from one side of the threat
    target_contact_of_source_contact1 = min([target_contact1, target_contact2],
                                            key=lambda c: c.distance(source_contact1))
    potential_path1 \
        = [source] + threat.get_boundary_between(source_contact1, target_contact_of_source_contact1) + [target]

    # possible path from the other side of the threat
    target_contact_of_source_contact2 = target_contact1 \
        if target_contact1 is not target_contact_of_source_contact1 else target_contact2
    potential_path2 \
        = [source] + threat.get_boundary_between(source_contact2, target_contact_of_source_contact2) + [target]

    # return the minimal path between the two
    min_path = min([potential_path1, potential_path2], key=lambda path: compute_path_length(path))
    return min_path, compute_path_length(min_path), 0


def single_threat_shortest_path_with_risk_constraint(
        source: Coord, target: Coord, threat: Threat, risk_limit: float
) -> Tuple[List[Coord], float, float]:
    """Computes the shortest path under a risk budget considering one threat

    There are three cases:
    1. if straight path is possible, do it. else:
    2. if risk limit is less than the distance between the contact points,
       the path consists a chord of length as the limit no matter where between the contact points. else:
    3. the path consists a chord of length as the limit is found by derivation of some function

    :param source: the source of the path
    :param target: the target of the path
    :param threat: the single threat
    :param risk_limit: the risk limit
    :return: the shortest path under the risk budget, its length and its risk
    """
    print(f'planning with risk limit {risk_limit} via one threat...')

    # check case 1
    risk_of_st_path = threat.compute_path_risk([source, target])
    if risk_of_st_path <= risk_limit:
        print('case 1: straight line between source and target is possible')
        return [source, target], source.distance(target), risk_of_st_path

    # compute the contact points and their distance
    s_contact1, s_contact2 = source.contact_points_with_circle(threat.center, threat.radius)
    t_contact2, t_contact1 = target.contact_points_with_circle(threat.center, threat.radius)
    s_contact, t_contact = min(zip([s_contact1, s_contact2], [t_contact1, t_contact2]),
                               key=lambda uv: uv[0].distance(uv[1]))

    contact_distance = s_contact.distance(t_contact)
    center = threat.center
    radius = threat.radius

    # check case 2
    if contact_distance >= risk_limit:
        print(f'case 2: the risk limit {risk_limit} is under the contact points distance {round(contact_distance, 2)}')

        p1, p2 = calculate_points_in_distance_on_circle(center, radius, s_contact, risk_limit)
        p = min([p1, p2], key=lambda p: p.distance(t_contact))

        path = [source] + threat.get_boundary_between(p, t_contact) + [target]

        return path, compute_path_length(path), threat.compute_path_risk(path)

    # solving case 3
    print(f'case 3: the risk limit {risk_limit} is over the contact points distance {round(contact_distance, 2)}')
    beta = calculate_angle_on_chord(risk_limit, radius)

    def L1(theta: float) -> float:
        entry_point = center.shift(distance=radius, angle=theta)
        exit_point = center.shift(distance=radius, angle=theta + beta)
        return source.distance(entry_point) + risk_limit + target.distance(exit_point)

    def L2(theta: float) -> float:
        entry_point = center.shift(distance=radius, angle=theta)
        exit_point = center.shift(distance=radius, angle=theta - beta)
        return source.distance(entry_point) + risk_limit + target.distance(exit_point)

    p1, p2 = calculate_points_in_distance_on_circle(center, radius, t_contact, risk_limit)
    chord_start_of_t_contact = min([p1, p2], key=lambda p: p.distance(source))

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

    entry_point = center.shift(distance=radius, angle=theta)
    exit_point = center.shift(distance=radius, angle=exit_point_angle)

    path = [source, entry_point, exit_point, target]
    return path, compute_path_length(path), threat.compute_path_risk(path)


def single_threat_safest_path_with_length_constraint(
        source: Coord, target: Coord, threat: Threat, length_limit: float
) -> Tuple[List[Coord], float, float]:
    """Computes the safest path under a length budget considering one threat

    There are three cases:
    1. if safe path is possible, do it. else:
    2. if length limit is less than the distance between the contact points,
       the path consists a chord of length as the limit no matter where between the contact points. else:
    3. the path consists a chord of total length as the limit is found by derivation of some function

    :param source: the source of the path
    :param target: the target of the path
    :param threat: the single threat
    :param length_limit: the length limit
    :return: the shortest path under the risk budget, its length and its risk
    """
    print(f'planning with length limit {length_limit}...')

    # check case 1
    path, length, risk = safest_path_single_threat(source, target, threat)
    if length <= length_limit:
        print('safe path between source and target is possible')
        return path, length, 0

    # compute the contact points and their distance
    s_contact1, s_contact2 = source.contact_points_with_circle(threat.center, threat.radius)
    t_contact2, t_contact1 = target.contact_points_with_circle(threat.center, threat.radius)
    s_contact, t_contact = min(zip([s_contact1, s_contact2], [t_contact1, t_contact2]),
                               key=lambda uv: uv[0].distance(uv[1]))

    contact_distance = s_contact.distance(t_contact)
    length_via_contact = source.distance(s_contact) + contact_distance + target.distance(t_contact)

    center = threat.center
    radius = threat.radius

    # check case 2
    if length_via_contact <= length_limit:
        print(
            f'the length limit {length_limit} is greater than the path via contact points {round(length_via_contact, 2)}')

        # TBD
        chord_length = length_limit - source.distance(s_contact)
        p1, p2 = calculate_points_in_distance_on_circle(center, radius, s_contact, 0)
        p = min([p1, p2], key=lambda p: p.distance(t_contact))
        boundary_between_points = threat.get_boundary_between(p, t_contact)

        # if the boundary between points is flipped
        if boundary_between_points[0].distance(source) > boundary_between_points[-1].distance(source):
            boundary_between_points = boundary_between_points[::-1]

        path = [source] + boundary_between_points + [target]

        return path, length_limit, chord_length

    # solving case 3
    # beta = calculate_angle_on_chord(risk_limit, radius)
    #
    # def L1(theta: float) -> float:
    #     entry_point = center.shift(distance=radius, angle=theta)
    #     exit_point = center.shift(distance=radius, angle=theta + beta)
    #     return source.distance(entry_point) + risk_limit + target.distance(exit_point)
    #
    # def L2(theta: float) -> float:
    #     entry_point = center.shift(distance=radius, angle=theta)
    #     exit_point = center.shift(distance=radius, angle=theta - beta)
    #     return source.distance(entry_point) + risk_limit + target.distance(exit_point)
    #
    # p1, p2 = calculate_points_in_distance_on_circle(center, radius, t_contact, risk_limit)
    # chord_start_of_t_contact = min([p1, p2], key=lambda p: p.distance(source))
    #
    # L_range = (calculate_directional_angle_of_line(start=center, end=s_contact),
    #            calculate_directional_angle_of_line(start=center, end=chord_start_of_t_contact))
    # L_range = L_range if L_range[0] < L_range[1] else (L_range[1], L_range[0])
    #
    # # if passing through x-axis
    # if L_range[0] + math.pi < L_range[1]:
    #     L_range = (L_range[1], L_range[0] + 2 * math.pi)
    #
    # theta1 = min(np.arange(L_range[0], L_range[1], 0.01), key=lambda theta: L1(theta))
    # theta2 = min(np.arange(L_range[0], L_range[1], 0.01), key=lambda theta: L2(theta))
    #
    # theta = theta1
    # exit_point_angle = theta + beta
    #
    # if L1(theta1) > L2(theta2):
    #     theta = theta2
    #     exit_point_angle = theta - beta
    #
    # entry_point = center.shift(distance=radius, angle=theta)
    # exit_point = center.shift(distance=radius, angle=exit_point_angle)
    #
    # path = [source, entry_point, exit_point, target]
    # return path, compute_path_length(path), risk_limit
    pass


def multiple_threats_safest_path_with_length_constraint(
        source: Coord, target: Coord, threats: Tuple[Threat], length_limit: float) -> Tuple[List[Coord], float, float]:
    pass


def multiple_threats_shortest_path_with_risk_constraint(
        source: Coord, target: Coord, threats: List[Threat], risk_limit: float, budgets) -> Tuple[List[Coord], float, float]:
    threat1, threat2 = threats
    centers_line = LineString([threat1.center, threat2.center])
    centers_angle = calculate_directional_angle_of_line(threat1.center, threat2.center)
    separation_angle = centers_angle + 0.5 * math.pi
    ch = threat1.polygon.union(threat2.polygon).convex_hull

    mid_mid_target = centers_line.intersection(threat1.polygon.exterior)
    distance_between_threats = threat1.center.distance(threat2.center) - (threat1.radius + threat2.radius)
    mid_mid_target = Coord(mid_mid_target.x, mid_mid_target.y).shift(distance=0.5 * distance_between_threats, angle=centers_angle)

    mid_targets = []
    i = 0
    while True:
        shifted = mid_mid_target.shift(distance=i, angle=separation_angle)
        if not ch.contains(shifted):
            break
        mid_targets.append(shifted)
        i += 10

    i = 0
    while True:
        shifted = mid_mid_target.shift(distance=i, angle=separation_angle + math.pi)
        if not ch.contains(shifted):
            break
        mid_targets.append(shifted)
        i += 10

    plt.scatter([p.x for p in mid_targets], [p.y for p in mid_targets])

    optional_paths = {mid_target: None for mid_target in mid_targets}

    for mid_target in mid_targets:
        path_to, length_to, risk_to = single_threat_shortest_path_with_risk_constraint(
            source, mid_target, threat1, risk_limit * budgets[0])
        path_from, length_from, risk_from = single_threat_shortest_path_with_risk_constraint(
            mid_target, target, threat2, risk_limit * budgets[1])
        optional_paths[mid_target] = {'path': path_to + path_from,
                                      'length': length_to + length_from,
                                      'risk': risk_to + risk_from}

    min_mid_target = min(mid_targets, key=lambda t: optional_paths[t]['length'])
    return optional_paths[min_mid_target]['path'], \
           optional_paths[min_mid_target]['length'], \
           optional_paths[min_mid_target]['risk']
