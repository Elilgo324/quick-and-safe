import math
import time
from typing import List, Tuple, Dict

import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point
from heapq import nsmallest
from tqdm import tqdm

from environment import Environment


class PRM:
    def __init__(self, env: Environment) -> None:
        self._env = env

        # neighborhood consts
        self._neighborhood_k = 5
        self._neighborhood_dist = 5000

        # init graph
        self._graph = nx.Graph()
        self._add_points(env.targets, is_target=True)

    @property
    def graph(self) -> nx.Graph():
        return self._graph

    def _add_points(self, points: List[Point], is_target: bool = False) -> None:
        for point in points:
            self._graph.add_node(f'({point.x},{point.y})', x=point.x, y=point.y, is_target=is_target)

    def extend_iterations(self, num_iterations: int, neighborhood_type: str = 'k') -> None:
        for _ in tqdm(range(num_iterations)):
            self._extend(neighborhood_type)

    def _k_neighborhood(self, point: Point) -> List[Tuple[str, Dict]]:
        def _k_nearest_key(point_xy) -> float:
            _, xy = point_xy
            dist = (xy['x'] - point.x) ** 2 + (xy['y'] - point.y) ** 2
            return dist if dist > 0 else math.inf

        k_nearest_nodes = nsmallest(self._neighborhood_k, self._graph.nodes(data=True), key=_k_nearest_key)
        return k_nearest_nodes

    def _dist_neighborhood(self, point: Point) -> List[Tuple[str, Dict]]:
        neighborhood_nodes = []
        for node_name, xy in self._graph.nodes(data=True):
            dist = ((xy['x'] - point.x) ** 2 + (xy['y'] - point.y) ** 2) ** 0.5
            if dist < self._neighborhood_dist:
                neighborhood_nodes.append((node_name, xy))

        return neighborhood_nodes

    def _extend(self, neighborhood_type: str) -> None:
        sample = self._env.sample()

        # add sample to graph
        sample_name = f'({sample.x},{sample.y})'
        self._graph.add_node(sample_name, x=sample.x, y=sample.y)

        # find near nodes to connect
        if neighborhood_type == 'k':
            near_nodes = self._k_neighborhood(sample)
        else:
            near_nodes = self._dist_neighborhood(sample)

        # add illegal edges with near group
        for node_name, node_data in near_nodes:
            x1, y1, x2, y2 = sample.x, sample.y, node_data['x'], node_data['y']
            if self._env.is_legal_edge(sample, Point(x2, y2)):
                weight = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                self._graph.add_edge(sample_name, node_name, x1=x1, x2=x2, y1=y1, y2=y2, weight=weight)

    def plot(self) -> None:
        # plot environment
        self._env.plot()

        # plot roadmap
        plt.title(f'roadmap with {len(self._graph.nodes)} nodes and {len(self._graph.edges)} edges', fontsize=20)

        if self._graph is not None:
            # plot edges
            for _, _, e_data in self._graph.edges(data=True):
                x1, x2, y1, y2 = e_data['x1'], e_data['x2'], e_data['y1'], e_data['y2']
                plt.plot([x1, x2], [y1, y2], color='green')

            # plot nodes
            for _, n_data in self._graph.nodes(data=True):
                x, y = n_data['x'], n_data['y']
                plt.scatter(x, y, color='black', s=60, zorder=7)
                plt.scatter(x, y, color='gray', s=50, zorder=8)


if __name__ == '__main__':
    num_nodes_list = list(range(100, 2100, 100))
    for num_nodes in num_nodes_list:
        # create environment
        env = Environment(num_targets=100)
        # env.plot()

        # create roadmap
        prm = PRM(env)
        prm.extend_iterations(num_nodes, neighborhood_type='k')
        prm.plot()
        plt.show()

        # compute distances
        graph = prm.graph
        targets = env.targets_names
        print(f'graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges')

        # dijkstra
        print('running dijkstra..')
        start = time.time()

        for target in targets:
            nx.single_source_dijkstra(source=target, G=graph)

        print(f'elapsed time is {(time.time() - start) / 60} m')

        # floyd warshall
        print('running floyd warshall..')
        start = time.time()

        nx.floyd_warshall(G=graph)

        print(f'elapsed time is {(time.time() - start) / 60} m')