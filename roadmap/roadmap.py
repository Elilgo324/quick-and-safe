from abc import ABC
from itertools import combinations
from typing import List, Tuple

import networkx as nx
from shapely.geometry import Point, LineString

from settings.environment import Environment
import matplotlib.pyplot as plt

EPSILON = 0.00001


class Roadmap(ABC):
    def __init__(self, environment: Environment) -> None:
        self._environment = environment

        # init graph with source and target
        self._graph = nx.Graph()
        self._add_points(environment.endpoints, is_endpoint=True)

    @property
    def graph(self) -> nx.Graph():
        return self._graph

    def _add_points(self, points: List[Point], is_endpoint: bool = False) -> None:
        for point in points:
            self._graph.add_node((point.x, point.y), x=point.x, y=point.y, is_endpoint=is_endpoint)

    def _add_edges(self, edges: List[Tuple[Point, Point]]) -> None:
        for edge in edges:
            p1, p2 = edge
            edge_line = LineString([p1, p2])
            length = edge_line.length
            risk = max([edge_line.intersection(threat).length for threat in self._environment.threats_polygons])
            self._add_points([p1, p2])
            self._graph.add_edge((p1.x, p1.y), (p2.x, p2.y), x1=p1.x, x2=p2.x, y1=p1.y, y2=p2.y,
                                 length=length, risk=risk + EPSILON * length)

    def _compute_path_length_and_risk(self, path: List[Tuple[float, float]]) -> Tuple[float, float]:
        path_length = path_risk = 0
        for p1, p2 in zip(path[:-1], path[1:]):
            path_length += self._graph[p1][p2]['length']
            path_risk += self._graph[p1][p2]['risk']
        return path_length, path_risk

    def shortest_path(self, weight: str = 'length') -> Tuple[List[Tuple[float, float]], float, float]:
        s, t = self._environment.source, self._environment.target
        path = nx.shortest_path(self._graph, weight=weight, source=(s.x, s.y), target=(t.x, t.y))
        path_length, path_risk = self._compute_path_length_and_risk(path)
        return path, path_length, path_risk

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
