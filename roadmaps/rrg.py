import math
from typing import List

from tqdm import tqdm

from environment.environment import Environment
from geometry.coord import Coord
from roadmaps.prm import PRM


class RRG(PRM):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        self._near_radius = 100
        self._steering_coefficient = 50

    def _near(self, point: Coord) -> List[Coord]:
        return [p for p in self.graph.nodes if p.distance_to(point) < self._near_radius]

    def _nearest(self, point: Coord) -> Coord:
        return min(self.graph.nodes, key=lambda p: point.distance_to(p))

    def add_samples(self, iterations: int) -> None:
        for _ in tqdm(range(iterations)):
            sample = self._environment.sample(is_safe_sample=False)
            nearest = self._nearest(sample)

            steered_sample = nearest.shifted(
                distance=self._steering_coefficient,
                angle=math.atan((sample.y - nearest.y) / (sample.x - nearest.x))
            )

            near = self._near(steered_sample)
            self._add_edges([(steered_sample, node) for node in near])
