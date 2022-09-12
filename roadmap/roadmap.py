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
LAYER_GRANULARITY = 1

class Roadmap(ABC):
    def __init__(self, environment: Environment) -> None:
        self._environment = environment

        # init graph with source and target
        self._graph = nx.Graph()
        self._add_points(environment.endpoints)

    @property
    def graph(self) -> nx.Graph():
        return self._graph

    def merge_graph(self, other: nx.Graph, merge_radius: float = 1) -> None:
        # add all edges from other graph
        self._add_edges([(Point(*u), Point(*v)) for u, v in other.edges])

        # add edge between close nodes from the graphs
        for u in other.nodes:
            u = Point(*u)
            for v in self.graph.nodes:
                v = Point(*v)
                if u.distance(v) < merge_radius:
                    self._add_edges([(u, v)])

    def refine_path(self, path: List[Point]) -> List[Point]:
        # compute risks table in O(path)
        risk_up_to = {point: 0 for point in path}
        for prev_p, cur_p in zip(path[:-1], path[1:]):
            cur_risk = self._environment.compute_segment_attributes(prev_p, cur_p)
            risk_up_to[cur_p] = risk_up_to[prev_p] + cur_risk

        # check if shortcuts available
        for i1, p1 in enumerate(path[:-1]):
            for i2, p2 in enumerate(path[i1::-1]):
                # length shortcut is sure. need to check if risk is not worse
                shortcut_attributes = self._environment.compute_segment_attributes(p1, p2)
                if shortcut_attributes['risk'] > risk_up_to[p2] - risk_up_to[p1]:
                    continue

                path = path[:i1 + 1] + path[i2:]
                break
        return path

    def _add_points(self, points: List[Point]) -> None:
        for point in points:
            self._graph.add_node((point.x, point.y))

    def _add_edges(self, edges: List[Tuple[Point, Point]]) -> None:
        for edge in edges:
            p1, p2 = edge
            attributes = self._environment.compute_segment_attributes(p1, p2)
            self._add_points([p1, p2])

            # add epsilon * length to risk in order to prefer shorter paths with same risk
            self._graph.add_edge((p1.x, p1.y), (p2.x, p2.y),
                                 length=attributes['length'],
                                 risk=attributes['risk'] + EPSILON * attributes['length'])

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
        layers_num = int((budget + 1) / LAYER_GRANULARITY)
        layers_graph = nx.Graph()

        # add nodes layers
        for layer in range(layers_num):
            for node in self.graph.nodes:
                # each node is (original x, original y, layer)
                layers_graph.add_node((*node, layer))

        # connect layers with edges
        for layer in range(layers_num):
            for edge_u, edge_v, edge_data in self.graph.edges(data=True):
                jump = ceil(edge_data[constraint] / LAYER_GRANULARITY)

                # skip if edge goes outside layers
                if layer + jump > layers_num:
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
                    plt.plot([x1, x2], [y1, y2], color='gray', linestyle='dashed', zorder=1)

            # plot nodes
            for x, y in self.graph.nodes:
                plt.scatter(x, y, color='black', s=20, zorder=7)
                plt.scatter(x, y, color='gray', s=10, zorder=8)
