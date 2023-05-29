import matplotlib.pyplot as plt

from environment.environment import Environment
from geometry.coord import Coord

if __name__ == '__main__':
    source = Coord(50, 200)
    target = Coord(950, 800)

    budget = 200

    environment = Environment(source, target, [])
    all_circles = Environment.create_disjoint_circles_in_range(num_circles=6)
    environment.circles = environment.filter_circles(source, target, all_circles)
    circles = environment.circles

    path1 = multiple_threats_shortest_path_with_budget_constraint(
        source, target, circles, budget, alphas=[budget / len(circles) for _ in circles])[0]
    # path2 = layers_multiple_threats_shortest_path_with_budget_constraint(
    #     source, target, circles, budget
    # )[0]

    for circle in all_circles:
        circle.plot('gray')
    environment.plot()

    path1.plot('green')
    # path2.plot('blue')

    plt.title('filtered circles in gray', fontsize=16)
    plt.savefig('multiple_circles_example.png', bbox_inches='tight')
