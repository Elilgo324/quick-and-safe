import copy
import math
import random
from random import randint, seed
from typing import List, Dict

import matplotlib.pyplot as plt
from shapely import MultiPoint
from shapely.geometry import Polygon

from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from geometry.segment import Segment


class Environment:
    def __init__(self, source: Coord, target: Coord, circles: List[Circle], env_range: (int, int) = (1000, 1000),
                 seed_value: int = 42, obstacles_idx: List[int] = None) -> None:
        if obstacles_idx is None:
            obstacles_idx = []
        self._obstacles_idx = obstacles_idx

        self._seed_value = seed_value
        seed(self._seed_value)

        self._source = source
        self._target = target
        self._x_range, self._y_range = env_range

        self._circles = circles

    @property
    def x_range(self) -> int:
        return self._x_range

    @property
    def y_range(self) -> int:
        return self._y_range

    @property
    def circles(self) -> List[Circle]:
        return self._circles

    @circles.setter
    def circles(self, circles: List[Circle]) -> None:
        self._circles = circles

    @property
    def shapely_circles(self) -> List[Polygon]:
        return [circle.inner_polygon for circle in self._circles]

    @property
    def source(self) -> Coord:
        return self._source

    @property
    def target(self) -> Coord:
        return self._target

    @property
    def endpoints(self) -> List[Coord]:
        return [self._source, self._target]

    def is_safe_point(self, point: Coord) -> bool:
        return all([not circle.contains(point) for circle in self.shapely_circles])

    def is_safe_edge(self, segment: Segment) -> bool:
        return all([not circle.intersects(segment) for circle in self.shapely_circles])

    def _create_circles(self, num_circles: int) -> None:
        self._circles = [Circle.generate_random_threat((self.x_range, self.y_range)) for _ in range(num_circles)]

    def create_disjoint_circles(self, num_circles: int) -> List[Circle]:
        circles = []
        for _ in range(num_circles):
            circles.append(Circle.generate_non_intersecting_random_circle(circles, (self.x_range, self.y_range)))
        return circles

    @staticmethod
    def create_disjoint_circles_in_range(source: Coord, target: Coord, num_circles: int,
                                         env_range: (int, int) = (1000, 1000)) -> List[Circle]:
        circles = [Circle(source, 1), Circle(target, 1)]
        for _ in range(num_circles):
            circles.append(Circle.generate_non_intersecting_random_circle(
                circles, env_range))
        return circles

    @staticmethod
    def create_separated_circles_in_range(source: Coord, target: Coord, num_circles: int,
                                          env_range: (int, int) = (1000, 1000)) -> List[Circle]:
        st_segment = Segment(source, target)
        separation_points = sorted([st_segment.sample() for _ in range(num_circles + 1)],
                                   key=lambda p: p.distance_to(source))
        # separation_points = st_segment.linsplit(num_circles + 1)
        intervals = [Segment(p1, p2) for p1, p2 in zip(separation_points[:-1], separation_points[1:])]
        circles = []
        for interval in intervals:
            center = interval.midpoint.shifted(distance=random.uniform(0, 100),
                                               angle=st_segment.angle + math.pi / 2 * ((-1) ** random.randint(1, 2)))
            radius = (interval.length - 10) / 2
            circles.append(Circle(center, radius))
        return circles

    @staticmethod
    def filter_circles(source: Coord, target: Coord, circles: List[Circle]) -> List[Circle]:
        ch = MultiPoint([source.to_shapely, target.to_shapely]).convex_hull
        prev_ch = None
        while ch != prev_ch:
            prev_ch = copy.deepcopy(ch)
            intersecting_circles = [circle for circle in circles if circle.to_shapely.intersects(ch)]
            circles_points = [source.to_shapely, target.to_shapely]
            for circle in intersecting_circles:
                circles_points += circle.to_shapely.boundary.coords
            ch = MultiPoint(circles_points).convex_hull
        return [circle for circle in circles if circle.to_shapely.intersects(ch)]

    def compute_segment_attributes(self, segment: Segment) -> Dict[str, float]:
        return {'length': segment.length,
                'risk': sum([
                    circle.path_intersection_length(Path([segment.start, segment.end])) if not i in self._obstacles_idx else 420_000
                    for i, circle in enumerate(self.circles)
                ])}

    def compute_path_attributes(self, path: Path) -> Dict[str, float]:
        segments_attributes = [self.compute_segment_attributes(s) for s in path.segments]
        return {'length': sum(attr['length'] for attr in segments_attributes),
                'risk': sum(attr['risk'] for attr in segments_attributes)}

    def sample(self, is_safe_sample: bool = True) -> Coord:
        rand_point = Coord(randint(0, self._x_range), randint(0, self._y_range))
        while is_safe_sample and not self.is_safe_point(rand_point):
            rand_point = Coord(randint(0, self._x_range), randint(0, self._y_range))
        return rand_point

    @staticmethod
    def sample_in_range(env_range: (int, int) = (1000, 1000)) -> Coord:
        return Coord(randint(0, env_range[0]), randint(0, env_range[1]))

    def plot(self) -> None:
        # plt.figure(figsize=(5, 5))
        plt.style.use('seaborn-whitegrid')
        plt.grid(True)
        plt.axis('equal')

        # plot threats
        for circle in self._circles:
            circle.plot()

        # plot source and target
        for endpoint in [self._source, self._target]:
            endpoint.plot()
