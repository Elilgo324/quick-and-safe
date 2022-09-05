from typing import Tuple, List

from shapely.geometry import LineString, Point
from scipy.optimize import fsolve
import math

from algorithms.geometric import contact_points_given_circle_and_point, is_left_side_of_line, shift_point, \
    calculate_angle_on_chord, calculate_angle_of_line
from settings.threat import Threat


def shortest_path_single_threat(
        source: Point, target: Point, threat: Threat) -> Tuple[List[Point], float, float]:
    """Calculates the shortest path considering one threat

    :param source: the source
    :param target: the target
    :param threat: a threat
    :return: shortest path between source and target, its length and risk
    """
    source_target_line = LineString([source, target])
    threat_intersection = LineString(source_target_line.intersection(threat.polygon))

    return [source, target], source_target_line.length, threat_intersection.length


def safest_path_single_threat(source: Point, target: Point, threat: Threat) -> Tuple[List[Point], float, float]:
    """Calculates the (shortest) safest path considering one threat

    :param source: the source
    :param target: the target
    :param threat: a threat
    :return: safest path between source and target, its length and risk
    """
    source_contacts = contact_points_given_circle_and_point(threat.center, threat.radius, source)
    target_contacts = contact_points_given_circle_and_point(threat.center, threat.radius, target)

    # check the safe paths via the two sides of the threat
    sort_key = lambda p: is_left_side_of_line(line_point1=source, line_point2=target, point=p)
    source_contact1, source_contact2 = sorted(source_contacts, key=sort_key)
    target_contact1, target_contact2 = sorted(target_contacts, key=sort_key)

    edge_points1 = [p for p in threat.boundary if not is_left_side_of_line(source_contact1, target_contact1, p)]
    potential_path1 = [source, source_contact1] + edge_points1 + [target_contact1, target]

    edge_points2 = [p for p in threat.boundary if is_left_side_of_line(source_contact2, target_contact2, p)]
    potential_path2 = [source, source_contact2] + edge_points2 + [target_contact2, target]

    min_path = min([potential_path1, potential_path2], key=lambda path: LineString(path).length)
    return min_path, LineString(min_path).length, 0


def single_threat_shortest_path_with_risk_constraint(
        source: Point, target: Point, threat: Threat, risk_limit: float) -> Tuple[List[Point], float, float]:
    """Calculates the shortest path with parallel chord under a risk constraint
    Notice this is not necessarily the general shortest path, as the chord can be non-parallel.

    :param source: the source
    :param target: the target
    :param threat: a threat
    :param risk_limit: the risk constraint
    :return: the shortest path with parallel chord under the risk constraint
    """
    source_target_line = LineString([source, target])

    # if not intersecting threat, return the direct line
    if not source_target_line.intersects(threat.polygon):
        return [source, target], source_target_line.length, 0

    # if intersection is under the risk limit, return the direct line
    intersection = source_target_line.intersection(threat.polygon)
    if intersection.length <= risk_limit:
        return [source, target], source_target_line.length, intersection.length

    # else, return the shortest path with a parallel chord with length as the risk limit
    angle_on_chord = calculate_angle_on_chord(risk_limit, threat.radius)
    angle_of_line = calculate_angle_of_line(source, target)

    angle_p1 = angle_of_line + (0.5 * math.pi - 0.5 * angle_on_chord)
    angle_p2 = angle_p1 + angle_on_chord

    # check the chords of both sides and take the minimal
    p1 = shift_point(point=threat.center, distance=threat.radius, angle=angle_p1)
    p2 = shift_point(point=threat.center, distance=threat.radius, angle=angle_p2)
    q1 = shift_point(point=threat.center, distance=threat.radius, angle=angle_p1 + math.pi)
    q2 = shift_point(point=threat.center, distance=threat.radius, angle=angle_p2 + math.pi)

    optional_path1 = [source, p1, p2, target]
    optional_path1.sort(key=lambda p: p.distance(source))
    optional_path2 = [source, q1, q2, target]
    optional_path2.sort(key=lambda p: p.distance(source))

    min_path = min([optional_path1, optional_path2], key=lambda path: LineString(path).length)
    return min_path, LineString(min_path).length, LineString(min_path[1:-1]).length


def single_threat_safest_path_with_length_constraint(
        source: Point, target: Point, threat: Threat, length_limit: float) -> Tuple[List[Point], float, float]:
    """Calculates the safest path with parallel chord under a length constraint
    Notice this is not necessarily the general safest path, as the chord can be non-parallel.

    :param source: the source
    :param target: the target
    :param threat: a threat
    :param length_limit: the length constraint
    :return: the safest path with parallel chord under the risk constraint
    """
    safest_path, safest_path_length, _ = safest_path_single_threat(source, target, threat)

    if safest_path_length <= length_limit:
        return safest_path, safest_path_length, 0

    r = threat.radius
    center = threat.center
    st_slope = (target.y - source.y) / (target.x - source.x)

    # solve 4 equations of 4 variables to get the points on the threat
    def equations(p):
        x1, y1, x2, y2 = p
        return ((x1 - center.x) ** 2 + (y1 - center.y) ** 2 - r ** 2,
                (x2 - center.x) ** 2 + (y2 - center.y) ** 2 - r ** 2,
                (y1 - y2) / (x1 - x2) - st_slope,
                math.sqrt((x1 - source.x) ** 2 + (y1 - source.y) ** 2) +
                math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) +
                math.sqrt((x2 - target.x) ** 2 + (y2 - target.y) ** 2) - length_limit)

    x1, y1, x2, y2 = fsolve(equations, (source.x, source.y, target.x, target.y))
    p1, p2 = Point(x1, y1), Point(x2, y2)
    path = [source, p1, p2, target]
    return path, LineString(path).length, p1.distance(p2)


def multiple_threats_safest_path_with_length_constraint(
        source: Point, target: Point, threats: Tuple[Threat], length_limit: float) -> Tuple[List[Point], float, float]:
    """Calculates the safest path with a risk constraint considering multiple threats

    :param source: the source
    :param target: the target
    :param threats: the threats
    :param length_limit: the risk constraint
    :return: the safest path with a risk constraint considering multiple threats
    """
    pass


def multiple_threats_shortest_path_with_risk_constraint(
        source: Point, target: Point, threats: Tuple[Threat], risk_limit: float) -> Tuple[List[Point], float, float]:
    """Calculates the shortest path with a risk constraint considering multiple threats

    :param source: the source
    :param target: the target
    :param threats: the threats
    :param risk_limit: the risk constraint
    :return: the shortest path with a risk constraint considering multiple threats
    """
    pass
