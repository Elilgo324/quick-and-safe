from random import randint, seed
from typing import List, Dict

import matplotlib.pyplot as plt
from shapely.geometry import Polygon

from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from geometry.segment import Segment


class Environment:
    def __init__(self, source: Coord, target: Coord, circles: List[Circle], env_range: (int, int) = (1000, 1000),
                 seed_value: int = 42) -> None:
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

    def _create_disjoint_threats(self, num_circles: int) -> None:
        for _ in range(num_circles):
            self._circles.append(Circle.generate_non_intersecting_random_circle(
                self.shapely_circles, (self.x_range, self.y_range)))

    def compute_segment_attributes(self, segment: Segment) -> Dict[str, float]:
        return {'length': segment.length,
                'risk': sum([circle.path_intersection(Path([segment.start, segment.end])) for circle in self.circles])}

    def compute_path_attributes(self, path: Path) -> Dict[str, float]:
        segments_attributes = [self.compute_segment_attributes(s) for s in path.segments]
        return {'length': sum(attr['length'] for attr in segments_attributes),
                'risk': sum(attr['risk'] for attr in segments_attributes)}

    def sample(self, is_safe_sample: bool = True) -> Coord:
        rand_point = Coord(randint(0, self._x_range), randint(0, self._y_range))
        while is_safe_sample and not self.is_safe_point(rand_point):
            rand_point = Coord(randint(0, self._x_range), randint(0, self._y_range))
        return rand_point

    def plot(self) -> None:
        plt.figure(figsize=(10, 10))
        plt.style.use('seaborn-whitegrid')
        plt.grid(True)
        plt.axis('equal')

        # plot threats
        for circle in self._circles:
            circle.plot()

        # plot source and target
        for endpoint in [self._source, self._target]:
            endpoint.plot()
