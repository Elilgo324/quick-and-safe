from algorithms.planning import single_threat_shortest_path_with_risk_constraint
from settings.coord import Coord
from settings.threat import Threat

import matplotlib.pyplot as plt


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


if __name__ == '__main__':
    one_threat_under_risk_budget()
    one_threat_under_length_budget()
