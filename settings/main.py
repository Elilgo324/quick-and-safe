import networkx as nx

from algorithms.geometric import contact_points_given_circle_and_point
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
    source = Coord(0, 0)
    target = Coord(1000, 1000)
    threat = Threat(center=Coord(300, 250), radius=250)
    env = Environment(source, target, num_threats=1, seed_value=27)
    env._threats = [threat]

    # prm = Grid(env)
    # prm.merge_graph(grid.graph, merge_radius=10)

    # rm = VisibilityRoadmap(env)
    # grid = Grid(env)
    # rm.merge_graph(grid.graph, merge_radius=10)

    # rm.plot(False)

    env.plot()

    c11, c12 = contact_points_given_circle_and_point(threat.center, threat.radius, source)
    c21, c22 = contact_points_given_circle_and_point(threat.center, threat.radius, target)

    plt.scatter(c11.x, c11.y, color='orange', zorder=10, s=50)
    plt.scatter(c12.x, c12.y, color='orange', zorder=10, s=50)
    plt.scatter(c21.x, c21.y, color='orange', zorder=10, s=50)
    plt.scatter(c22.x, c22.y, color='orange', zorder=10, s=50)

    budget = 140
    # path, length, risk, time = rm.constrained_shortest_path(budget=budget)
    path, length, risk = single_threat_shortest_path_with_risk_constraint(source, target, threat, budget, env)

    # rm.plot(display_edges=False)
    plt.plot([p.x for p in path], [p.y for p in path],
             color='green', linestyle='dashed', linewidth=3)

    # plt.title(f'roadmap with {len(rm._graph.nodes)} nodes and {len(rm._graph.edges)} edges', fontsize=18, y=1.07)
    plt.legend(handles=[Patch(color='gold', label='endpoints'),
                        Patch(color='red', label=f'{len(env.threats)} threats'),
                        Line2D([0], [0], color='blue', linestyle='dashed',
                               label=f'constrained path (length: {length}, risk: {risk}, computation time: {0 + 0}s)')],
               fontsize=14, frameon=True, loc='upper center', bbox_to_anchor=(0.5, 1.07), ncol=2, fancybox=True)

    plt.savefig(f'../plots/constrained_path_example_{budget}.png')
    plt.show()


    # visibility = VisibilityRoadmap(env)
    # pos = {c: c for c in visibility.graph.nodes}
    #
    # nx.draw(visibility.graph, pos=pos)
    # plt.scatter(env.source.x, env.source.y, color='red', zorder=10)
    # plt.scatter(env.target.x, env.target.y, color='red', zorder=11)
    # plt.show()
    # print(nx.shortest_path(G=visibility.graph, source=env.source.xy, target=env.target.xy))
    # visibility.constrained_shortest_path(weight='length', constraint='risk', budget=100)
