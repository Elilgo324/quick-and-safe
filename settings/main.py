import math

import networkx as nx

from algorithms.geometric import calculate_points_in_distance_on_circle, calculate_directional_angle_of_line
from algorithms.planning import single_threat_shortest_path_with_risk_constraint
from roadmap.grid import Grid
from roadmap.prm import PRM
from roadmap.rrg import RRG
from settings.coord import Coord
from settings.environment import Environment
from settings.threat import Threat
from roadmap.visibility_roadmap import VisibilityRoadmap
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from settings.threat import Threat

if __name__ == '__main__':
    center = Coord(0, 0)
    radius = 4
    source = Coord(-10, -2)
    target = Coord(5, 2)
    risk_limit = 6
    threat = Threat(center, radius)
    env = Environment(source=Coord(0, 0), target=Coord(1000, 1000), num_threats=1, seed_value=27)
    env._threats = [threat]


    def path_length(theta, limit):
        entrance_point = center.shift(distance=radius, angle=theta)

        from_source = source.distance(entrance_point)

        second_point1, second_point2 = calculate_points_in_distance_on_circle(center, radius, entrance_point, limit)
        to_target = min(second_point1.distance(target), second_point2.distance(target))

        return from_source + limit + to_target

    all_thetas = [(x*2*math.pi) / 360 for x in range(360)]

    source_contact1, source_contact2 = source.contact_points_with_circle(center, radius)
    target_contact1, target_contact2 = target.contact_points_with_circle(center, radius)

    source_contact = min([source_contact1, source_contact2], key=lambda x: x.distance(target))
    target_contact = min([target_contact1, target_contact2], key=lambda x: x.distance(source))

    p1,p2 = calculate_points_in_distance_on_circle(
        center, radius, source_contact, risk_limit)
    chord_point_of_source_contact = min([p1,p2], key=lambda x: x.distance(target))

    p1, p2 = calculate_points_in_distance_on_circle(
        center, radius, target_contact, risk_limit)
    chord_point_of_target_contact = min([p1, p2], key=lambda x: x.distance(source))

    c1_theta = calculate_directional_angle_of_line(source_contact, center)
    c2_theta = calculate_directional_angle_of_line(chord_point_of_target_contact, center)

    print(c1_theta)
    print(c2_theta)

    valid_thetas = [theta for theta in all_thetas if min(c1_theta, c2_theta) < theta < max(c1_theta, c2_theta)]

    distances = [path_length(theta, risk_limit) for theta in valid_thetas]
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title(f'path length as function of entry point angle from center')
    plt.plot([x / math.pi * 180 for x in valid_thetas], distances)

    plt.subplot(1, 2, 2)
    plt.title(f'shortest length under budget of {risk_limit}')
    min_theta = min(valid_thetas, key=lambda x: path_length(x, risk_limit))

    X, Y = center.buffer(radius).exterior.coords.xy
    plt.plot(X, Y)
    plt.scatter(source.x, source.y, color='blue')
    plt.scatter(target.x, target.y, color='blue')
    entry = center.shift(distance=radius, angle=min_theta)
    second_point1, second_point2 = calculate_points_in_distance_on_circle(center, radius, entry, risk_limit)
    path = [source, entry,
            min([second_point1, second_point2], key=lambda x: x.distance(target)),
            target]
    plt.plot([c.x for c in path], [c.y for c in path])


    plt.show()
