from typing import Tuple

import numpy as np

from algorithms.multiple_threats import multiple_threats_shortest_path
from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path

EPSILON = 1
INF = 1000


def two_threats_shortest_path(source: Coord, target: Coord, circle1: Circle, circle2: Circle) \
        -> Tuple[Path, float, float]:
    return multiple_threats_shortest_path(source, target, [circle1, circle2])


def _considering_only_first_circle(source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float) \
        -> Tuple[Path, float, float]:
    path, length, risk = single_threat_shortest_path_with_budget_constraint(target, source, circle1, budget)
    return path, length, risk + circle2.path_intersection(path)


def _considering_both_circles_blackbox_method(source: Coord, target: Coord, circle1: Circle, circle2: Circle,
                                              budget: float,
                                              alpha: float = 0.5
                                              ) -> Tuple[Path, float, float]:
    b1, b2 = alpha * budget, (1 - alpha) * budget

    partition = Circle.calculate_partition_between_circles(circle1, circle2, source, target, [circle1, circle2])

    def L(d: float) -> Path:
        mid_target = partition.start.shifted(d, partition.angle)
        return Path.concat_paths(
            single_threat_shortest_path_with_budget_constraint(source, mid_target, circle1, b1)[0],
            single_threat_shortest_path_with_budget_constraint(mid_target, target, circle2, b2)[0]
        )

    path = min([L(d) for d in np.arange(0, partition.length, 1)], key=lambda p: p.length)

    return path, path.length, circle1.path_intersection(path) + circle2.path_intersection(path)


def two_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circle1: Circle, circle2: Circle, budget: float
) -> Tuple[Path, float, float]:
    direct_result = two_threats_shortest_path(source, target, circle1, circle2)
    if direct_result[2] <= budget:
        return direct_result

    circle1, circle2 = min([(circle1, circle2), (circle2, circle1)],
                           key=lambda c1c2: c1c2[0].distance_to(source) + c1c2[1].distance_to(target))

    # assumption: only "relevant" circles are included in the planning
    # (i.e. the endpoints are located in different sides of the partition)
    path, length, risk = min([_considering_both_circles_blackbox_method(source, target, circle1, circle2, budget, alpha)
                              for alpha in np.arange(0, 1.01, 0.1)], key=lambda plr: plr[1])
    return path, length, risk


import matplotlib.pyplot as plt

if __name__ == '__main__':
    c1 = Circle(Coord(200, 100), 100)
    c2 = Circle(Coord(400, 125), 75)
    source = Coord(0, 0)
    target = Coord(500, 200)
    budget = 200
    path, length, risk = two_threats_shortest_path_with_budget_constraint(
        source, target, c1, c2, budget)
    title = f'length {round(length, 2)} risk {round(risk, 2)}'
    plt.title(title)
    plt.gca().set_aspect('equal', adjustable='box')
    path.plot()
    source.plot()
    target.plot()
    c1.plot()
    c2.plot()

    # alphas = np.arange(0, 1.01, 0.1)
    # als = []
    # lengths = []
    # for alpha in tqdm(alphas):
    #     try:
    #         path, length, _ = _considering_both_circles_blackbox_method(
    #             source, target, c1, c2, budget, alpha)
    #         als.append(alpha)
    #         lengths.append(length)
    #     except:
    #         pass
    # plt.plot(als, lengths)

    plt.show()
    # plt.savefig(title + '.png')

# if __name__ == '__main__':
#     c1 = Circle(Coord(200, 100), 100)
#     c2 = Circle(Coord(400, 125), 70)
#     source = Coord(0, 125)
#     target = Coord(600, 50)
#     budget = 300
#     alpha = 0.75
#     # path, length, risk = two_threats_shortest_path_with_budget_constraint_blackbox_method(
#     #     source, target, c1, c2, budget, 0.5)
#     plt.subplot(2, 1, 1)
#     # plt.title(f'length {round(length, 2)} risk {round(risk, 2)}')
#     title = f'length as function of mid target shift (alpha={alpha} budget={budget})'
#     plt.title(title)
#     plt.gca().set_aspect('equal', adjustable='box')
#     # path.plot()
#     source.plot()
#     target.plot()
#     c1.plot()
#     c2.plot()
#
#     plt.subplot(2, 1, 2)
#
#     _considering_both_circles_blackbox_method(source, target, c1, c2, budget, alpha)
#
#     # plt.show()
#     plt.savefig(title + '.png')
