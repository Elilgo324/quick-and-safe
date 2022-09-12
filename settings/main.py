from roadmap.prm import PRM
from settings.environment import Environment
from roadmap.visibility_roadmap import VisibilityRoadmap
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from shapely.geometry import Point

if __name__ == '__main__':
    env = Environment(source=Point(100, 150), target=Point(900, 600), num_threats=10, seed_value=27)
    prm = PRM(env)
    prm.add_samples(100)
    # prm.plot(True)
    # plt.show()
    path = prm.shortest_path()
    path = prm.constrained_shortest_path(budget=100)
