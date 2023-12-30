import itertools
from abc import ABC
from math import ceil
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from tqdm import tqdm

from algorithms.multiple_threats import multiple_threats_shortest_path
from environment.environment import Environment
from geometry.coord import Coord
from geometry.path import Path
from geometry.segment import Segment

EPSILON = 0.0000001
LAYER_GRANULARITY = 10


class Roadmap:
    def __init__(self, environment: Environment) -> None:
        self._environment = environment

        # init graph with source and target
        self._graph = nx.Graph()
        self._add_points(environment.endpoints)

    @property
    def graph(self) -> nx.Graph():
        return self._graph

    def merge_graph(self, other: nx.Graph, merge_radius: float = 10) -> None:
        # add all edges from other graph
        self._add_edges(list(other.edges))

        # add edge between close nodes from the graphs
        for u, v in itertools.product(self.graph.nodes, other.nodes):
            if u.distance_to(v) < merge_radius:
                self._add_edges([(u, v)])

    def _compute_path_length_and_risk(self, path: Path) -> Tuple[float, float]:
        path_risk = 0
        for p1, p2 in zip(path.coords[:-1], path.coords[1:]):
            path_risk += self._graph[p1][p2]['risk']
        return path.length, path_risk

    def refine_path(self, path: Path) -> List[Coord]:
        # compute risks table in O(path)
        risk_up_to = {point: 0 for point in path}
        for prev_p, cur_p in zip(path.coords[:-1], path.coords[1:]):
            cur_risk = self._environment.compute_segment_attributes(Segment(prev_p, cur_p))['risk']
            risk_up_to[cur_p] = risk_up_to[prev_p] + cur_risk

        # check if shortcuts available
        for i1, p1 in enumerate(path.coords[:-1]):
            for i2, p2 in enumerate(path.coords[i1::-1]):
                # length shortcut is sure. need to check if risk is not worse
                shortcut_risk = self._environment.compute_segment_attributes(Segment(p1, p2))['risk']
                if shortcut_risk > risk_up_to[p2] - risk_up_to[p1]:
                    continue

                path = path[:i1 + 1] + path[i2:]
                break
        return path

    def _add_points(self, points: List[Coord]) -> None:
        self._graph.add_nodes_from(points)

    def _add_edges(self, edges: List[Tuple[Coord, Coord]]) -> None:
        for (u, v) in edges:
            attributes = self._environment.compute_segment_attributes(Segment(u, v))
            self._add_points([u, v])

            # add epsilon * length to risk in order to prefer shorter paths with same risk
            self._graph.add_edge(u, v,
                                 length=attributes['length'],
                                 risk=attributes['risk'] + EPSILON * attributes['length'])

    def shortest_path(self, weight: str = 'length') -> Tuple[Path, float, float]:
        source, target = self._environment.source, self._environment.target

        path = Path([p for p in nx.shortest_path(self.graph, weight=weight, source=source, target=target)])

        path_length, path_risk = self._compute_path_length_and_risk(path)
        return path, path_length, path_risk

    def constrained_shortest_path(self, budget: float = 0, weight: str = 'length', constraint: str = 'risk') -> Tuple[
        Path, float, float]:

        source, target = self._environment.source, self._environment.target

        if budget == 0:
            for e in self._graph.edges:
                if self._graph[e[0]][e[1]]['risk'] > 0:
                    self._graph[e[0]][e[1]]['length'] = 100_000
            return self.shortest_path()

        layers_num = int((budget + 1) / LAYER_GRANULARITY)
        layers_graph = nx.DiGraph()

        # add nodes layers
        print('adding nodes layers..')
        for layer in tqdm(range(layers_num)):
            for node in self.graph.nodes:
                # each node is (original x, original y, layer)
                layers_graph.add_node((node, layer))

        # connect layers with edges
        print('connecting layers with edges..')
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

        print('calculating shortest path..')
        path = nx.shortest_path(layers_graph, weight=weight, source=(source, 0), target=virtual_target)
        path = Path([p for p, _ in path[:-1]])

        path_length, path_risk = self._compute_path_length_and_risk(path)
        return path, path_length, path_risk

    def plot(self, display_edges: bool = False) -> None:
        # plot environment
        self._environment.plot()

        # plot roadmaps
        if self.graph is not None:
            # plot edges
            if display_edges:
                for u, v in self._graph.edges:
                    plt.plot([u.x, v.x], [u.y, v.y], color='gray', linestyle='dashed', zorder=1)

            # plot nodes
            for node in self.graph.nodes:
                node.plot()
