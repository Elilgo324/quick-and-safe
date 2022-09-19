import networkx as nx

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
    center = Coord(5, 5)
    radius = 3
    source = Coord(-2, 6)
    target = Coord(8.3, 1)
    risk_limit = 0.5
    threat = Threat(center, radius)
    env = Environment(source=Coord(0, 0), target=Coord(1000, 1000), num_threats=1, seed_value=27)
    env._threats = [threat]

    path, length, risk = single_threat_shortest_path_with_risk_constraint(source, target, threat, risk_limit, env)

    plt.figure(figsize=(5, 5))
    plt.title('contact calculation example', fontsize=16)
    plt.grid(True)
    plt.axis('equal')
    plt.scatter([p.x for p in path], [p.y for p in path], color='orange', zorder=10)

    plt.plot(*center.buffer(radius).exterior.xy, color='blue', zorder=1)

    plt.show()
