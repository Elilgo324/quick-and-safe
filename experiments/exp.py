import matplotlib.pyplot as plt

from algorithms.layers import layers_multiple_threats_shortest_path_with_budget_constraint
from environment.environment import Environment
from geometry.circle import Circle
from geometry.coord import Coord

# if __name__ == '__main__':
#     source = Environment.sample_in_range()
#     target = Environment.sample_in_range()
#
#     source = Coord(50, 200)
#     target = Coord(950, 800)
#
#     budget = 20
#
#     environment = Environment(source, target, [])
#     all_circles = Environment.create_separated_circles_in_range(source, target, num_circles=5)
#     environment.circles = environment.filter_circles(source, target, all_circles)
#     circles = environment.circles
#
#     path1 = multiple_threats_shortest_path_with_budget_constraint(
#         source, target, circles, budget, alphas=[budget / len(circles) for _ in circles])[0]
#     path2 = layers_multiple_threats_shortest_path_with_budget_constraint(
#         source, target, circles, budget
#     )[0]
#
#     for circle in all_circles:
#         circle.plot('gray')
#     environment.plot()
#
#     path1.plot('green')
#     path2.plot('blue')
#
#     plt.title('multiple circles comparison example ', fontsize=16)
#     plt.savefig('multiple_circles_comparison_example.png')
#     # plt.show()

if __name__ == '__main__':
    source = Coord(0, 200)
    target = Coord(800, 30)

    budget = 200

    environment = Environment(source, target, [])
    all_circles = [Circle(Coord(300, 100), 201), Circle(Coord(700, 250), 140), Circle(Coord(680, 50), 50)]
    environment.circles = environment.filter_circles(source, target, all_circles)
    circles = environment.circles

    # path1 = multiple_threats_shortest_path_with_budget_constraint(
    #     source, target, circles, budget, alphas=[budget / len(circles) for _ in circles])[0]
    path2 = layers_multiple_threats_shortest_path_with_budget_constraint(
        source, target, circles, budget
    )[0]

    for circle in all_circles:
        circle.plot('gray')
    environment.plot()

    # path1.plot('green')
    path2.plot('blue')

    plt.title('multiple circles comparison example ', fontsize=16)
    # plt.savefig('multiple_circles_comparison_example.png')
    plt.show()
