import math
from random import uniform, randint
from typing import List

import networkx as nx
from shapely.geometry import Polygon, Point, LineString
from heapq import nsmallest
from tqdm import tqdm


class ProbRoadmap:
    def __init__(self, x_range: int, y_range: int, obstacles: List[Polygon]) -> None:
        self._x_range = x_range
        self._y_range = y_range
        self._obstacles = obstacles
        self._graph = nx.Graph()
        self._k = 5

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

    def add_points(self, points: List[Point]) -> None:
        for point in points:
            self._graph.add_node(f'{point.x}_{point.y}', x=point.x, y=point.y)

    def extend_iterations(self, num_iterations: int) -> None:
        for _ in tqdm(range(num_iterations)):
            self._extend()

    def _sample(self) -> Point:
        return Point(randint(0, self._x_range), randint(0, self._y_range))

    def _extend(self):
        sample = self._sample()
        while self._sample_is_in_obstacle(sample):
            sample = self._sample()

        self._graph.add_node(f'{sample.x}_{sample.y}', x=sample.x, y=sample.y)

        def _k_nearest_key(point_xy):
            _, xy = point_xy
            dist = (xy['x'] - sample.x) ** 2 + (xy['y'] - sample.y)
            return dist if dist > 0 else math.inf

        k_nearest_nodes = nsmallest(self._k, self._graph.nodes(data=True), key=_k_nearest_key)

        for node_name, node_data in k_nearest_nodes:
            if self._is_legal_edge(sample, Point(node_data['x'], node_data['y'])):
                self._graph.add_edge(f'{sample.x}_{sample.y}', node_name,
                                     x1=sample.x, x2=node_data['x'], y1=sample.y, y2=node_data['y'])
