import random

import matplotlib.pyplot as plt

from environment.environment import Environment
from geometry.coord import Coord

if __name__ == '__main__':
    print('running 10 circles experiment')
    source = Coord(50, 50)
    target = Coord(950, 950)

    random.seed(40)

    all_circles = Environment.create_disjoint_circles_in_range(source, target, num_circles=10)
    # filtered_circles = Environment.filter_circles(source, target, all_circles)
    environment = Environment(source, target, all_circles)

    plt.title('50 circles experiment example', fontsize=16)
    environment.plot()
    # plt.show()
    plt.savefig('50 circles experiment example.png')
