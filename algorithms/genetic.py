from typing import List, Tuple

import matplotlib.pyplot as plt

from environment.environment import Environment
from genetic_repo.MOEAD4MOSPP import main
from geometry.circle import Circle
from geometry.coord import Coord
from geometry.path import Path
from roadmaps.rrg import RRG


# https://github.com/Xavier-MaYiMing/The-MOEAD-for-the-multi-objective-shortest-path-problem


def genetic_multiple_threats_shortest_path_with_budget_constraint(
        source: Coord, target: Coord, circles: List[Circle], budget: float) -> Tuple[Path, float, float]:
    # test_network = {
    #     0: {1: [62, 50], 2: [44, 90], 3: [67, 10]},
    #     1: {0: [62, 50], 2: [33, 25], 4: [52, 90]},
    #     2: {0: [44, 90], 1: [33, 25], 3: [32, 10], 4: [52, 40]},
    #     3: {0: [67, 10], 2: [32, 10], 4: [54, 100]},
    #     4: {1: [52, 90], 2: [52, 40], 3: [54, 100]},
    # }

    environment = Environment(source, target, circles)
    rrg = RRG(environment)
    rrg.add_samples(1000)
    graph = rrg.graph

    source_node = source
    destination_node = target

    network = {n: {} for n in graph.nodes}
    for u, v, data in graph.edges(data=True):
        network[u][v] = [data['length'], data['risk']]
        network[v][u] = [data['length'], data['risk']]

    results = main(network, source_node, destination_node, 20, network_as_grpah=graph)
    print(f'num of solutions {len(results)}')
    valid_results = [result for result in results if result['objective'][1] < budget]
    result = min(valid_results, key=lambda result: result['objective'][0])
    print(result)
    objectives = result['objective']

    return Path(result['path']), objectives[0], objectives[1]


if __name__ == '__main__':
    source = Coord(50, 200)
    target = Coord(950, 800)

    budget = 400

    environment = Environment(source, target, [])
    all_circles = Environment.create_separated_circles_in_range(source, target, num_circles=5)
    environment.circles = environment.filter_circles(source, target, all_circles)
    circles = environment.circles

    path1 = genetic_multiple_threats_shortest_path_with_budget_constraint(
        source, target, circles, budget)[0]

    print(path1)

    for circle in all_circles:
        circle.plot('gray')
    environment.plot()

    path1.plot('green')
    plt.show()
    # plt.title('multiple circles comparison example ', fontsize=16)
    # plt.savefig('multiple_circles_comparison_example.png')
