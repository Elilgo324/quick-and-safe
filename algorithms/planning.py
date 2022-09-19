import itertools
from typing import Tuple, List
from itertools import product, combinations
from shapely.geometry import LineString, Point
from scipy.optimize import minimize_scalar
import math
from settings.environment import Environment
from settings.threat import Threat
from algorithms.geometric import is_left_side_of_line, \
    calculate_angle_on_chord, calculate_angle_of_line
from settings.coord import Coord
from settings.threat import Threat

EPSILON = 7


def compute_path_length(path: List[Coord]) -> float:
    return sum([c1.distance(c2) for c1, c2 in zip(path[:-1], path[1:])])


def shortest_path_single_threat(
        source: Coord, target: Coord, threat: Threat) -> Tuple[List[Coord], float, float]:
    source_target_line = LineString([source, target])
    threat_intersection = LineString(source_target_line.intersection(threat.polygon))

    return [source, target], source_target_line.length, threat_intersection.length


def safest_path_single_threat(source: Coord, target: Coord, threat: Threat) -> Tuple[List[Coord], float, float]:
    source_contact1, source_contact2 = source.contact_points_with_circle(threat.center, threat.radius)
    target_contact1, target_contact2 = target.contact_points_with_circle(threat.center, threat.radius)

    edge_points1 = [p for p in threat.boundary if not is_left_side_of_line(source_contact1, target_contact1, p)]
    potential_path1 = [source, source_contact1] + edge_points1 + [target_contact1, target]

    edge_points2 = [p for p in threat.boundary if is_left_side_of_line(source_contact2, target_contact2, p)]
    potential_path2 = [source, source_contact2] + edge_points2 + [target_contact2, target]

    min_path = min([potential_path1, potential_path2], key=lambda path: LineString(path).length)
    return min_path, LineString(min_path).length, 0


def single_threat_shortest_path_with_risk_constraint(
        source: Coord, target: Coord, threat: Threat, risk_limit: float, environment: Environment
) -> Tuple[List[Coord], float, float]:
    print(f'planning with risk limit {risk_limit}...')
    s_contact1, s_contact2 = source.contact_points_with_circle(threat.center, threat.radius)
    t_contact1, t_contact2 = target.contact_points_with_circle(threat.center, threat.radius)

    contact_distance = min(s_contact1.distance(t_contact2), s_contact2.distance(t_contact1))

    # if chord in range of contact points
    if contact_distance >= risk_limit:
        print(f'contact points distance {round(contact_distance, 2)} is above limit {risk_limit}')

        if s_contact1.distance(t_contact2) <= s_contact2.distance(t_contact1):
            s_contact = s_contact1
            t_contact = t_contact2
        else:
            s_contact = s_contact2
            t_contact = t_contact1

        boundary_between_points = threat.get_boundary_between(s_contact, t_contact)
        path = [source] + boundary_between_points + [target]
        attributes = environment.compute_path_attributes(path)

        return path, attributes['length'], attributes['risk']

    print('finding best chord...')
    boundary = threat.get_buffered_boundary(0.1)
    optional_chords = list(product(boundary, boundary))

    # filter chords with length not (close to) equal budget
    optional_chords = [
        chord for chord in optional_chords if (abs(chord[0].distance(chord[1]) - risk_limit) < EPSILON)
    ]

    # filter chords that intersect circle
    optional_chords = [
        chord for chord in optional_chords if not (
                LineString([source, chord[0]]).intersects(threat.polygon)
                or LineString([target, chord[1]]).intersects(threat.polygon)
        )
    ]

    optional_paths = [[source, chord[0], chord[1], target] for chord in optional_chords]
    
    # create optional paths with walking on boundary, and add binary search

    path = min(optional_paths, key=compute_path_length)
    path_attributes = environment.compute_path_attributes(path)
    return path, path_attributes['length'], path_attributes['risk']


def single_threat_safest_path_with_length_constraint(
        source: Coord, target: Coord, threat: Threat, length_limit: float) -> Tuple[List[Coord], float, float]:
    pass


def multiple_threats_safest_path_with_length_constraint(
        source: Coord, target: Coord, threats: Tuple[Threat], length_limit: float) -> Tuple[List[Coord], float, float]:
    pass


def multiple_threats_shortest_path_with_risk_constraint(
        source: Coord, target: Coord, threats: Tuple[Threat], risk_limit: float) -> Tuple[List[Coord], float, float]:
    pass
