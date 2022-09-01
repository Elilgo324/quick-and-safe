from abc import ABC
from itertools import combinations
from typing import List, Tuple

import networkx as nx
from shapely.geometry import Point, LineString

from settings.environment import Environment
import matplotlib.pyplot as plt

EPSILON = 0.000001


class Roadmap(ABC):
    def __init__(self, environment: Environment) -> None:
        self._environment = environment

        # init graph with targets
        self._graph = nx.Graph()
        self._add_points(environment.targets, is_target=True)

        self._tsp_shortest_graph = None
        self._tsp_safest_graph = None

    @property
    def graph(self) -> nx.Graph():
        return self._graph

    def _add_points(self, points: List[Point], is_target: bool = False) -> None:
        for point in points:
            self._graph.add_node((point.x, point.y), x=point.x, y=point.y, is_target=is_target)

    def _add_edges(self, edges: List[Tuple[Point, Point]]) -> None:
        for edge in edges:
            p1, p2 = edge
            edge_line = LineString([p1, p2])
            length = edge_line.length
            risk = max([edge_line.intersection(threat).length for threat in self._environment.threats_polygons])
            self._add_points([p1, p2])
            self._graph.add_edge((p1.x, p1.y), (p2.x, p2.y), x1=p1.x, x2=p2.x, y1=p1.y, y2=p2.y,
                                 length=length, risk=risk + EPSILON * length)

    def _construct_tsp_shortest_graph(self) -> None:
        if self._tsp_shortest_graph is None:
            self._tsp_shortest_graph = nx.Graph()
            for p1, p2 in combinations(self._environment.targets, 2):
                p1,p2 = (p1.x, p1.y), (p2.x, p2.y)
                shortest_path = nx.shortest_path(self._graph, source=p1, target=p2, weight='length')

                length, risk = 0, 0
                for q1, q2 in zip(shortest_path[:-1], shortest_path[1:]):
                    length += self._graph[q1][q2]['length']
                    risk += self._graph[q1][q2]['risk']

                self._tsp_shortest_graph.add_edge(
                    (p1[0], p1[1]), (p2[0], p2[1]), length=length, risk=risk, path=shortest_path)

    def _construct_tsp_safest_graph(self) -> None:
        if self._tsp_safest_graph is None:
            self._tsp_safest_graph = nx.Graph()
            for p1, p2 in combinations(self._environment.targets, 2):
                p1,p2 = (p1.x, p1.y), (p2.x, p2.y)
                safest_path = nx.shortest_path(self._graph, source=p1, target=p2, weight='risk')

                length, risk = 0, 0
                for q1, q2 in zip(safest_path[:-1], safest_path[1:]):
                    length += self._graph[q1][q2]['length']
                    risk += self._graph[q1][q2]['risk']

                self._tsp_safest_graph.add_edge(
                    (p1[0], p1[1]), (p2[0], p2[1]), length=length, risk=risk, path=safest_path)

    def shortest_tour(self) -> Tuple[List[Tuple[float, float]], float, float]:
        self._construct_tsp_shortest_graph()
        tour = nx.approximation.christofides(self._tsp_shortest_graph, weight='length')

        tour_length, tour_risk = 0, 0
        for p1, p2 in zip(tour[:-1], tour[1:]):
            tour_length += self._tsp_shortest_graph[p1][p2]['length']
            tour_risk += self._tsp_shortest_graph[p1][p2]['risk']

        return tour, round(tour_length, 2), round(tour_risk, 2)

    def safest_tour(self) -> Tuple[List[Tuple[float, float]], float, float]:
        self._construct_tsp_safest_graph()
        tour = nx.approximation.christofides(self._tsp_safest_graph, weight='risk')

        actual_tour = []
        tour_length, tour_risk = 0, 0
        for p1, p2 in zip(tour[:-1], tour[1:]):
            tour_length += self._tsp_safest_graph[p1][p2]['length']
            tour_risk += self._tsp_safest_graph[p1][p2]['risk']
            actual_tour.extend(self._tsp_safest_graph[p1][p2]['path'])

        return actual_tour, round(tour_length, 2), round(tour_risk, 2)

    def plot(self, display_edges: bool = False) -> None:
        # plot settings
        self._environment.plot()

        # plot roadmap
        if self._graph is not None:
            if display_edges:
                # plot edges
                for _, _, e_data in self._graph.edges(data=True):
                    x1, x2, y1, y2 = e_data['x1'], e_data['x2'], e_data['y1'], e_data['y2']
                    plt.plot([x1, x2], [y1, y2], color='green', linestyle='dashed')

            # plot nodes
            for _, n_data in self._graph.nodes(data=True):
                x, y = n_data['x'], n_data['y']
                plt.scatter(x, y, color='black', s=20, zorder=7)
                plt.scatter(x, y, color='gray', s=10, zorder=8)
