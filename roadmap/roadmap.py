from abc import ABC
from time import time
from itertools import combinations
from math import ceil
from typing import List, Tuple

import networkx as nx
from shapely.geometry import Point, LineString

from settings.environment import Environment
import matplotlib.pyplot as plt

EPSILON = 0.0000001


class Roadmap(ABC):
    def __init__(self, environment: Environment) -> None:
        self._environment = environment

        # init graph with source and target
        self._graph = nx.Graph()
        self._add_points(environment.endpoints)

    @property
    def graph(self) -> nx.Graph():
        return self._graph

    def _add_points(self, points: List[Point]) -> None:
        for point in points:
            self._graph.add_node((point.x, point.y), x=point.x, y=point.y)

    def _add_edges(self, edges: List[Tuple[Point, Point]]) -> None:
        for edge in edges:
            p1, p2 = edge
            edge_line = LineString([p1, p2])
            length = edge_line.length
            risk = max([edge_line.intersection(threat).length for threat in self._environment.threats_polygons])
            self._add_points([p1, p2])

            # add epsilon * length to risk in order to prefer shorter paths with same risk
            self._graph.add_edge((p1.x, p1.y), (p2.x, p2.y), length=length, risk=risk + EPSILON * length)

    def _compute_path_length_and_risk(self, path: List[Tuple[float, float]]) -> Tuple[float, float]:
        path_length = path_risk = 0
        for p1, p2 in zip(path[:-1], path[1:]):
            path_length += self._graph[p1][p2]['length']
            path_risk += self._graph[p1][p2]['risk']
        return round(path_length, 3), round(path_risk, 3)

    def shortest_path(self, weight: str = 'length') -> Tuple[List[Tuple[float, float]], float, float, float]:
        s, t = self._environment.source, self._environment.target

        start = time()
        path = nx.shortest_path(self._graph, weight=weight, source=(s.x, s.y), target=(t.x, t.y))
        computation_time = time() - start

        path_length, path_risk = self._compute_path_length_and_risk(path)
        return path, path_length, path_risk, round(computation_time, 3)

    def constrained_shortest_path(self, weight: str = 'length', constraint: str = 'risk', budget: float = 0) -> Tuple[
        List[Tuple[float, float]], float, float, float]:
        s, t = self._environment.source, self._environment.target

        start = time()
        layers_num = int(budget) + 1
        layers_graph = nx.Graph()

        # add nodes layers
        for layer in range(layers_num):
            for node in self.graph.nodes:
                # each node is (original x, original y, layer)
                layers_graph.add_node((*node, layer))

        # connect layers with edges
        for layer in range(layers_num):
            for edge_u, edge_v, edge_data in self.graph.edges(data=True):
                jump = ceil(edge_data[constraint])

                # skip if edge goes outside layers
                if layer + jump > int(budget) + 1:
                    continue

                layers_graph.add_edge((*edge_u, layer), (*edge_v, layer + jump))

        # connect all targets to virtual target
        virtual_target = 'virtual-target'
        layers_graph.add_node(virtual_target)
        for layer in range(layers_num):
            layers_graph.add_edge((t.x, t.y, layer), virtual_target)

        path = nx.shortest_path(layers_graph, weight=weight, source=(s.x, s.y, 0), target=virtual_target)
        path = [(x, y) for x, y, _ in path[:-1]]
        computation_time = time() - start

        path_length, path_risk = self._compute_path_length_and_risk(path)
        return path, path_length, path_risk, round(computation_time, 3)

    def plot(self, display_edges: bool = False) -> None:
        # plot settings
        self._environment.plot()

        # plot roadmap
        if self.graph is not None:
            if display_edges:
                # plot edges
                for u, v in self._graph.edges:
                    x1, y1 = u
                    x2, y2 = v
                    plt.plot([x1, x2], [y1, y2], color='green', linestyle='dashed')

            # plot nodes
            for x, y in self.graph.nodes:
                plt.scatter(x, y, color='black', s=20, zorder=7)
                plt.scatter(x, y, color='gray', s=10, zorder=8)
