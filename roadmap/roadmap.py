import itertools
from abc import ABC
from time import time
from math import ceil
from typing import List, Tuple

import networkx as nx

from geometry.coord import Coord
from environment.environment import Environment
import matplotlib.pyplot as plt

EPSILON = 0.0000001
LAYER_GRANULARITY = 1


class Roadmap(ABC):
    def __init__(self, environment: Environment) -> None:
        """Init roadmap

        :param environment: the environment
        """
        self._environment = environment

        # init graph with source and target
        self._graph = nx.Graph()
        self._add_points(environment.endpoints)

    @property
    def graph(self) -> nx.Graph():
        """Gets the graph of the roadmap

        :return: the graph of the roadmap
        """
        return self._graph

    def merge_graph(self, other: nx.Graph, merge_radius: float = 10) -> None:
        """Merges other graph with the roadmap's graph by a given radius

        :param other: other graph
        :param merge_radius: radius to connect nodes from both graphs
        """
        # add all edges from other graph
        self._add_edges([(Coord(*u), Coord(*v)) for u, v in other.edges])

        # add edge between close nodes from the graphs
        for u, v in itertools.product(self.graph.nodes, other.nodes):
            u, v = Coord(*u), Coord(*v)
            if u.distance(v) < merge_radius:
                self._add_edges([(u, v)])

    def _compute_path_length_and_risk(self, path: List[Coord]) -> Tuple[float, float]:
        """Computes the length and the risk of a given path

        :param path: the path
        :return: the length and the risk of the path
        """
        path_length = path_risk = 0
        for p1, p2 in zip(path[:-1], path[1:]):
            path_length += self._graph[p1.xy][p2.xy]['length']
            path_risk += self._graph[p1.xy][p2.xy]['risk']
        return round(path_length, 3), round(path_risk, 3)

    def refine_path(self, path: List[Coord]) -> List[Coord]:
        """Refines path with shortcuts if available

        :param path: the path
        :return: path with shortcuts if available
        """
        # compute risks table in O(path)
        risk_up_to = {point: 0 for point in path}
        for prev_p, cur_p in zip(path[:-1], path[1:]):
            cur_risk = self._environment.compute_segment_attributes(prev_p, cur_p)['risk']
            risk_up_to[cur_p] = risk_up_to[prev_p] + cur_risk

        # check if shortcuts available
        for i1, p1 in enumerate(path[:-1]):
            for i2, p2 in enumerate(path[i1::-1]):
                # length shortcut is sure. need to check if risk is not worse
                shortcut_risk = self._environment.compute_segment_attributes(p1, p2)['risk']
                if shortcut_risk > risk_up_to[p2] - risk_up_to[p1]:
                    continue

                path = path[:i1 + 1] + path[i2:]
                break
        return path

    def _add_points(self, points: List[Coord]) -> None:
        """Adds points to roadmap

        :param points: points to add
        """
        self._graph.add_nodes_from([point.xy for point in points])

    def _add_edges(self, edges: List[Tuple[Coord, Coord]]) -> None:
        """Adds edges to roadmap

        :param edges: edges to add
        """
        for (u, v) in edges:
            attributes = self._environment.compute_segment_attributes(u, v)
            self._add_points([u, v])

            # add epsilon * length to risk in order to prefer shorter paths with same risk
            self._graph.add_edge(u.xy, v.xy,
                                 length=attributes['length'],
                                 risk=attributes['risk'] + EPSILON * attributes['length'])

    def shortest_path(self, weight: str = 'length') -> Tuple[List[Coord], float, float, float]:
        """Computes the shortest path according given weight

        :param weight: a given weight
        :return: the shortest path according given weight
        """
        source, target = self._environment.source.xy, self._environment.target.xy

        start = time()
        path = [Coord(*p) for p in nx.shortest_path(self.graph, weight=weight, source=source, target=target)]
        computation_time = time() - start

        path_length, path_risk = self._compute_path_length_and_risk(path)
        return path, path_length, path_risk, round(computation_time, 3)

    def constrained_shortest_path(self, weight: str = 'length', constraint: str = 'risk', budget: float = 0) -> Tuple[
        List[Coord], float, float, float]:
        """Computes the constrained shortest path given a weight, a constraint and a budget
        This function uses a non-accurate and time expensive logic of layers graph

        :param weight: the weight
        :param constraint: the constraint
        :param budget: the constraint budget
        :return: the constrained shortest path
        """
        source, target = self._environment.source.xy, self._environment.target.xy

        start = time()
        layers_num = int((budget + 1) / LAYER_GRANULARITY)
        layers_graph = nx.DiGraph()

        # add nodes layers
        for layer in range(layers_num):
            for node in self.graph.nodes:
                # each node is (original x, original y, layer)
                layers_graph.add_node((node, layer))

        # connect layers with edges
        for layer in range(layers_num):
            for u, v, edge_data in self.graph.edges(data=True):
                jump = ceil(round(edge_data[constraint] / LAYER_GRANULARITY, 3))

                # skip if edge goes outside layers
                if layer + jump > layers_num:
                    continue

                layers_graph.add_edge((u, layer), (v, layer + jump), length=edge_data['length'], risk=edge_data['risk'])
                layers_graph.add_edge((v, layer), (u, layer + jump), length=edge_data['length'], risk=edge_data['risk'])

        # connect all targets to virtual target
        virtual_target = 'virtual-target'
        layers_graph.add_node(virtual_target)
        for layer in range(layers_num):
            layers_graph.add_edge((target, layer), virtual_target, length=0, risk=0)

        path = nx.shortest_path(layers_graph, weight=weight, source=(source, 0), target=virtual_target)
        path = [Coord(*p) for p, _ in path[:-1]]
        computation_time = time() - start

        path_length, path_risk = self._compute_path_length_and_risk(path)
        return path, path_length, path_risk, round(computation_time, 3)

    def plot(self, display_edges: bool = False) -> None:
        """Plots environment and graph

        :param display_edges: if to display the edges of the graph
        """
        # plot environment
        self._environment.plot()

        # plot roadmap
        if self.graph is not None:
            # plot edges
            if display_edges:
                for u, v in self._graph.edges:
                    plt.plot([u[0], v[0]], [u[1], v[1]], color='gray', linestyle='dashed', zorder=1)

            # plot nodes
            for n in self.graph.nodes:
                plt.scatter(n[0], n[1], color='black', s=20, zorder=7)
                plt.scatter(n[0], n[1], color='gray', s=10, zorder=8)
