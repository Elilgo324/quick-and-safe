import math
from random import uniform, randint
from typing import List, Callable, Tuple, Dict

import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, LineString
from heapq import nsmallest
from tqdm import tqdm


class PRM:
    def __init__(self, x_range: int, y_range: int, obstacles: List[Polygon], targets: List[Point]) -> None:
        self._x_range = x_range
        self._y_range = y_range
        self._obstacles = obstacles

        # neighborhood consts
        self._neighborhood_k = 5
        self._neighborhood_dist = 10

        # init graph
        self._graph = nx.Graph()
        self.add_points(targets, is_target=True)

    @property
    def graph(self) -> nx.Graph():
        return self._graph

    def _sample_is_in_obstacle(self, sample: Point) -> bool:
        for obstacle in self._obstacles:
            if obstacle.contains(sample):
                return True
        return False

    def _is_legal_edge(self, point1, point2):
        line = LineString([point1, point2])
        for obstacle in self._obstacles:
            if line.intersects(obstacle):
                return False
        return True

    def add_points(self, points: List[Point], is_target: bool = False) -> None:
        for point in points:
            self._graph.add_node(f'({point.x},{point.y})', x=point.x, y=point.y, is_target=is_target)

    def extend_iterations(self, num_iterations: int) -> None:
        for _ in tqdm(range(num_iterations)):
            self._extend()

    def _sample(self) -> Point:
        return Point(randint(0, self._x_range), randint(0, self._y_range))

    def _k_neighborhood(self, point: Point) -> List[Tuple[str, Dict]]:
        def _k_nearest_key(point_xy):
            _, xy = point_xy
            dist = (xy['x'] - point.x) ** 2 + (xy['y'] - point.y)
            return dist if dist > 0 else math.inf

        k_nearest_nodes = nsmallest(self._neighborhood_k, self._graph.nodes(data=True), key=_k_nearest_key)
        return k_nearest_nodes

    def _dist_neighborhood(self, point: Point) -> List[Tuple[str, Dict]]:
        neighborhood_nodes = []
        for node_name, xy in self._graph.nodes(data=True):
            dist = ((xy['x'] - point.x) ** 2 + (xy['y'] - point.y)) ** 0.5
            if dist < self._neighborhood_dist:
                neighborhood_nodes.append((node_name, xy))

        return neighborhood_nodes

    def _extend(self, neighborhood: Callable = _dist_neighborhood):
        sample = self._sample()
        while self._sample_is_in_obstacle(sample):
            sample = self._sample()

        # add sample to graph
        sample_name = f'({sample.x},{sample.y})'
        self._graph.add_node(sample_name, x=sample.x, y=sample.y)

        # find near nodes to connect
        near_nodes = neighborhood(sample)

        for node_name, node_data in near_nodes:
            x1, x2, y1, y2 = sample.x, sample.y, node_data['x'], node_data['y']
            if self._is_legal_edge(sample, Point(x2, y2)):
                self._graph.add_edge(sample_name, node_name, x1=x1, x2=x2, y1=y1, y2=y2)

    def plot(self):
        # plot roadmap
        if self._graph is not None:
            for _, _, e_data in self._graph.edges(data=True):
                x1, x2, y1, y2 = e_data['x1'], e_data['x2'], e_data['y1'], e_data['y2']
                plt.plot([x1, x2], [y1, y2], color='green')
                plt.scatter([x1, x2], [y1, y2], color='black', s=60, zorder=7)
                plt.scatter([x1, x2], [y1, y2], color='gray', s=50, zorder=8)
