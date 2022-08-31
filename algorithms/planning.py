import math
from typing import Tuple, List

from shapely.geometry import LineString, Point

from algorithms.geometric import contact_points_given_circle_and_point, is_left_side_of_line, shift_point, \
    calculate_angle_on_chord, calculate_angle_of_line


def shortest_path_single_threat(
        source: Point, target: Point, threat_center: Point, threat_radius: float) -> List[Point]:
    return [source, target]


def safest_path_single_threat(source: Point, target: Point, threat_center: Point, threat_radius: float) -> List[Point]:
    threat = threat_center.buffer(threat_radius)
    threat_points = [Point(*p) for p in threat.exterior.coords]
    source_contacts = contact_points_given_circle_and_point(threat_center, threat_radius, source)
    target_contacts = contact_points_given_circle_and_point(threat_center, threat_radius, target)

    source_contact1 = min(
        source_contacts, key=lambda p: is_left_side_of_line(line_point1=source, line_point2=target, point=p))
    target_contact1 = min(
        target_contacts, key=lambda p: is_left_side_of_line(line_point1=source, line_point2=target, point=p))
    edge_points = [p for p in threat_points if not is_left_side_of_line(source_contact1, target_contact1, p)]
    potential_path1 = [source, source_contact1] + edge_points + [target_contact1, target]

    source_contact2 = max(
        source_contacts, key=lambda p: is_left_side_of_line(line_point1=source, line_point2=target, point=p))
    target_contact2 = max(
        target_contacts, key=lambda p: is_left_side_of_line(line_point1=source, line_point2=target, point=p))
    edge_points = [p for p in threat_points if is_left_side_of_line(source_contact2, target_contact2, p)]
    potential_path2 = [source, source_contact2] + edge_points + [target_contact2, target]

    return min([potential_path1, potential_path2], key=lambda path: LineString(path).length)


def single_threat_shortest_path_with_risk_constraint(
        source: Point, target: Point, threat_center: Point, threat_radius: float, risk_limit: float) -> List[Point]:
    threat = threat_center.buffer(threat_radius)
    source_target_line = LineString([source, target])

    if not source_target_line.intersects(threat):
        return [source, target]

    if 2*threat_radius <= risk_limit:
        return [source, target]

    angle_of_chord = calculate_angle_on_chord(risk_limit, threat_radius)
    angle_of_line = calculate_angle_of_line(source, target)

    angle_p1 = angle_of_line + (0.5 * math.pi - 0.5 * angle_of_chord)
    angle_p2 = angle_p1 + angle_of_chord
    p1 = shift_point(point=threat_center, distance=threat_radius, angle=angle_p1)
    p2 = shift_point(point=threat_center, distance=threat_radius, angle=angle_p2)

    angle_q1 = -(math.pi - 0.5 * angle_of_chord - angle_of_line)
    angle_q2 = angle_q1 - angle_of_chord
    q1 = shift_point(point=threat_center, distance=threat_radius, angle=angle_p1 + math.pi)
    q2 = shift_point(point=threat_center, distance=threat_radius, angle=angle_p2 + math.pi)

    optional_path1 = [source, p1, p2, target]
    optional_path1.sort(key=lambda p:p.distance(source))
    optional_path2 = [source, q1, q2, target]
    optional_path2.sort(key=lambda p:p.distance(source))

    return min([optional_path1, optional_path2], key=lambda path: LineString(path).length)


def single_threat_safest_path_with_length_constraint(
        source: Point, target: Point, threat_center: Point, threat_radius: float, length_limit: float) -> List[Point]:
    safest_path = safest_path_single_threat(source, target, threat_center, threat_radius)

    if LineString(safest_path).length <= length_limit:
        return safest_path

    pass


def multiple_threats_safest_path_with_length_constraint(
        source: Point, target: Point, threat_centers: Tuple[Point], threat_rs: Tuple[float],
        length_limit: float) -> List[Point]:
    pass


def multiple_threats_shortest_path_with_risk_constraint(
        source: Point, target: Point, threat_centers: Tuple[Point], threat_rs: Tuple[float],
        risk_limit: float) -> List[Point]:
    pass
