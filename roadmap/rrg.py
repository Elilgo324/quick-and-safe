import math
from time import time
from typing import List, Tuple, Dict

from shapely.geometry import Point
from heapq import nsmallest

from roadmap.roadmap import Roadmap
from settings.coord import Coord
from settings.environment import Environment
from tqdm import tqdm


class RRG(Roadmap):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        self._near_radius = 10
        self._steering_coefficient = 5

    def _near(self, point: Coord) -> List[Coord]:
        return [Coord(*p) for p in self.graph.nodes if Coord(*p).distance(point) < self._near_radius]

    def _nearest(self, point: Coord) -> Coord:
        return min([Coord(*p) for p in self.graph.nodes], key=lambda p:point.distance(p))

    def add_samples(self, iterations: int) -> float:
        start = time()
        for _ in tqdm(range(iterations)):
            sample = self._environment.sample(is_safe_sample=False)
            nearest = self._nearest(sample)

            steered_sample = nearest.shift(
                distance=self._steering_coefficient,
                angle=math.atan((sample.y - nearest.y)/(sample.x - nearest.x))
            )

            near = self._near(steered_sample)
            self._add_edges([(steered_sample, node) for node in near])

        return round(time() - start, 3)


