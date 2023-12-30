import itertools
from typing import List, Tuple

from environment.environment import Environment
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from geometry.segment import Segment
from roadmaps.roadmap import Roadmap
from roadmaps.rrg import RRG

import matplotlib.pyplot as plt


def rrg_layers_multiple_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circles: List[Circle], budget: float, obstacles_idx: List[int] = None) -> Tuple[Path, float, float]:
    print('running layers algorithm')
    if obstacles_idx is None:
        obstacles_idx = []

    environment = Environment(source, target, circles, obstacles_idx=obstacles_idx)
    rrg = RRG(environment)
    rrg.add_samples(2000)

    return rrg.constrained_shortest_path(budget=budget)

def exaustive_layers_multiple_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circles: List[Circle], budget: float, obstacles_idx: List[int] = None) -> Tuple[Path, float, float]:
    if obstacles_idx is None:
        obstacles_idx = []

    print('running visibility algorithm')
    environment = Environment(source, target, circles)
    roadmap = Roadmap(environment)

    split_per_circle = {circle: circle.linsplit(32) for circle in circles}

    for i_circle, circle in enumerate(circles):
        if i_circle in obstacles_idx:
            continue
        split = split_per_circle[circle]
        for p1, p2 in itertools.product(split, split):
            if p1 == p2:
                continue
            roadmap._add_edges([(p1, p2)])

    for circle1, circle2 in itertools.product(circles, circles):
        if circle1 == circle2:
            continue
        split1 = split_per_circle[circle1]
        split2 = split_per_circle[circle2]
        for p1, p2 in itertools.product(split1, split2):
            if environment.compute_segment_attributes(Segment(p1, p2))['risk'] == 0:
                roadmap._add_edges([(p1, p2)])

    for circle in circles:
        split = split_per_circle[circle]
        for p in split:
            if environment.compute_segment_attributes(Segment(source, p))['risk'] == 0:
                roadmap._add_edges([(source, p)])
            if environment.compute_segment_attributes(Segment(p, target))['risk'] == 0:
                roadmap._add_edges([(p, target)])

    return roadmap.constrained_shortest_path(budget=budget)