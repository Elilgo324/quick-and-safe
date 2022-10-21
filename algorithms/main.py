from algorithms.planning import single_threat_shortest_path_with_risk_constraint, \
    multiple_threats_shortest_path_with_risk_constraint
from settings.coord import Coord
from settings.threat import Threat

import matplotlib.pyplot as plt
import numpy as np


def one_threat_under_risk_budget():
    target = Coord(-0.5, 4)
    source = Coord(5, 3)
    threat = Threat(center=Coord(3, 4), radius=1.8)

    plt.figure(figsize=(10, 10))

    plt.title('shortest path via one threat under risk limit', fontsize=16)

    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat.boundary], [p.y for p in threat.boundary])

    plt.gca().set_aspect('equal', adjustable='box')

    for risk_limit in [1, 2, 3, 4]:
        path, length, risk = single_threat_shortest_path_with_risk_constraint(source, target, threat, risk_limit)
        plt.plot([p.x for p in path], [p.y for p in path], label=f'risk limit {risk_limit}, length {round(length, 2)}')

    plt.legend(fontsize=14)
    plt.show()


def one_threat_under_length_budget():
    target = Coord(-0.5, 4)
    source = Coord(5, 3)
    threat = Threat(center=Coord(3, 4), radius=1.8)

    plt.figure(figsize=(10, 10))

    plt.title('safest path via one threat under length limit', fontsize=16)

    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat.boundary], [p.y for p in threat.boundary])

    plt.gca().set_aspect('equal', adjustable='box')

    for risk_limit in [1, 2, 3, 4]:
        path, length, risk = single_threat_shortest_path_with_risk_constraint(source, target, threat, risk_limit)
        plt.plot([p.x for p in path], [p.y for p in path], label=f'risk limit {risk_limit}, length {round(length, 2)}')

    plt.legend(fontsize=14)
    plt.show()


def two_symetric_threats():
    plt.figure(figsize=(10, 7))
    plt.suptitle('two symetric threats', fontsize=22, y=0.95)
    source = Coord(0, 5)
    target = Coord(30, 5)
    threat1 = Threat(center=Coord(10, 4), radius=4.5)
    threat2 = Threat(center=Coord(20, 4), radius=4.5)
    risk_limits = [1, 5, 10, 15]

    plt.subplot(2,1,1)
    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    for risk_limit in risk_limits:
        path, length, risk = multiple_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                                 risk_limit, budgets=[0.5, 0.5])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'risk limit {round(risk, 2)}, length {round(length, 2)}')

    plt.legend(fontsize=14)

    plt.subplot(2,1,2)

    lengths = {}
    for b in np.arange(0, 1.1, 0.1):
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = multiple_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in [1, 5]:
        plt.plot(list(np.arange(0, 1.1, 0.1)), lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.legend()
    plt.xlim([0,1])
    plt.ylim([30,31])
    plt.show()

def same_threats_farther_source():
    pass


if __name__ == '__main__':
    # one_threat_under_risk_budget()
    # one_threat_under_length_budget()
    # two_symetric_threats()
    # same_threats_farther_source()
    # smaller_threat()
    # non_symetric_but_same_side()
    # non_symetric_not_same_side()


