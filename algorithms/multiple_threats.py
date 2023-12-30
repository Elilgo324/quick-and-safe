import itertools
from typing import List, Tuple

from tqdm import tqdm

from algorithms.single_threat import single_threat_shortest_path_with_budget_constraint
from algorithms.two_threats import two_threats_shortest_path_with_budget_constraint
from environment.environment import Environment
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path


def multiple_threats_shortest_path(source: Coord, target: Coord, circles: List[Circle]) -> Tuple[Path, float, float]:
    path = Path([source, target])

    circles_intersection_length = sum(
        [circle.path_intersection_length(path) for circle in circles]
    )

    return path, path.length, circles_intersection_length


def multiple_threats_shortest_path_with_budget_constraint_given_order_and_budgets(
        source: Coord, target: Coord, circles: List[Circle], budget: float, alphas: List[float]) -> Tuple[
    Path, float, float]:
    print('running analytical algorithm')
    if len(circles) == 0:
        return multiple_threats_shortest_path(source, target, [])

    if len(circles) == 1:
        return single_threat_shortest_path_with_budget_constraint(source, target, circles[0], budget)

    if len(circles) == 2:
        return two_threats_shortest_path_with_budget_constraint(source, target, circles[0], circles[1], budget)

    # create layers of partition lines linsplit
    partitions = [Circle.calculate_partition_between_circles(c1, c2, source, target, circles)
                  for c1, c2 in zip(circles[:-1], circles[1:])]
    layers = [[p for p in partition.linsplit(amount=21) if all([not circle.contains(p) for circle in circles])] for
              partition in partitions] + [[target]]

    path_to_point = {}

    # handle the connection between source and first layer
    for p in layers[0]:
        path_to_point[p] = \
        single_threat_shortest_path_with_budget_constraint(source, p, circles[0], alphas[0] * budget)[0]

        # if solution of 1 circle intersects other circle, it is not optimal
        if any([path_to_point[p].intersects(circle) and circle != circles[0] for circle in circles]):
            path_to_point[p] = Path([Coord(0, 0), Coord(42_000, 42_00), p])

    # handle the connections between the layers and between the last and the target
    for alpha, circle, prev_layer, cur_layer in zip(alphas[1:], circles[1:], layers[:-1], layers[1:]):
        for prev_p, cur_p in itertools.product(prev_layer, cur_layer):
            path_to_cur_p = single_threat_shortest_path_with_budget_constraint(
                prev_p, cur_p, circle, alpha * budget)[0]

            # if solution of 1 circle intersects other circle, it is not optimal
            if any([path_to_cur_p.intersects(c) and c != circle for c in circles]):
                path_to_cur_p = Path([prev_p, Coord(42_000, 42_00), cur_p])

            path_to_cur_p = Path.concat_paths(path_to_point[prev_p], path_to_cur_p)

            # add path-to-point to dictionary if does not exist or it is shorter
            if not cur_p in path_to_point:
                path_to_point[cur_p] = path_to_cur_p
            else:
                path_to_point[cur_p] = path_to_cur_p if path_to_point[cur_p].length > path_to_cur_p.length \
                    else path_to_point[cur_p]

    path = path_to_point[target]
    environment = Environment(source, target, circles)
    spent_budget = environment.compute_path_attributes(path)['risk']
    print(f'spent_budget {spent_budget}')

    return path, path.length, spent_budget


def multiple_threats_shortest_path_with_budget_constraint_given_budget(
        source: Coord, target: Coord, circles: List[Circle], budget: float, alphas: List[float]) -> Tuple[
    Path, float, float]:
    circles_alphas = zip(circles, alphas)
    all_orders = list(itertools.permutations(circles_alphas))

    all_results = []
    for order in tqdm(all_orders):
        circles, alphas = zip(*order)
        all_results.append(multiple_threats_shortest_path_with_budget_constraint_given_order_and_budgets(
            source, target, circles, budget, alphas))

    print(f'{result[0]},length={result[1]}' for result in list(all_results))
    return min(all_results, key=lambda r: r[1])


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # c1 = Circle(Coord(200, 100), 100)
    # c2 = Circle(Coord(400, 125), 75)
    # c3 = Circle(Coord(600, 90), 90)
    # c4 = Circle(Coord(800, 200), 50)
    circles = [Circle(Coord(500, 400), 200),
               Circle(Coord(380, 700), 110),
               Circle(Coord(790, 580), 130)]
    source = Coord(0, 500)
    target = Coord(1000, 500)
    budget = 0
    alphas = [0.4, 0.4, 0.2]
    path, length, risk = multiple_threats_shortest_path_with_budget_constraint_given_budget(
        source, target, circles, budget, alphas)
    title = f'length {round(length, 2)} risk {round(risk, 2)}'
    plt.title(title)
    plt.gca().set_aspect('equal', adjustable='box')
    path.plot()
    source.plot()
    target.plot()
    [c.plot() for c in circles]
    plt.show()
