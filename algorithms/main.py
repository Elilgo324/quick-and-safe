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


def two_symmetric_threats():
    plt.figure(figsize=(10, 7))
    plt.suptitle('scenario 1: two symmetric threats', fontsize=22, y=0.98)
    source = Coord(0, 1)
    target = Coord(1000, 1)
    radius = 100
    threat1 = Threat(center=Coord(300, 0), radius=radius)
    threat2 = Threat(center=Coord(700, 0), radius=radius)
    risk_limits = [0.5 * radius, radius, 2 * radius, 3 * radius]

    plt.subplot(2, 1, 2)
    plt.grid(True)
    plt.title('shortest paths')

    lengths = {}
    bs = np.arange(0, 1.01, 0.1)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = multiple_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.ylim([1000, 1050])
    plt.xlim([0, 1])
    plt.legend()

    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.title('path length as function of first threat budget')

    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    for risk_limit in risk_limits:
        ib = min(range(len(bs)), key=lambda i: lengths[risk_limit][i])
        b = bs[ib]
        path, length, risk = multiple_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                                 risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'risk {round(risk, 2)}, length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.show()


def same_threats_farther_source():
    plt.figure(figsize=(10, 7))
    plt.suptitle('scenario 2: farther source', fontsize=22, y=0.95)
    source = Coord(-500, 1)
    target = Coord(1000, 1)
    radius = 100
    threat1 = Threat(center=Coord(300, 0), radius=radius)
    threat2 = Threat(center=Coord(700, 0), radius=radius)
    risk_limits = [0.5 * radius, radius, 2 * radius, 3 * radius]

    plt.subplot(2, 1, 2)
    plt.grid(True)

    lengths = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = multiple_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    y_limit = [45, 55]
    plt.ylim(y_limit)
    rad_prop = threat1.radius / (threat1.radius + threat2.radius)
    plt.plot([rad_prop, rad_prop], y_limit, color='black', linestyle='--', label='radius prop.')
    plt.legend(fontsize=12)

    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    for risk_limit in risk_limits:
        ib = min(range(len(bs)), key=lambda i: lengths[risk_limit][i])
        b = bs[ib]
        path, length, risk = multiple_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                                 risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'risk {round(risk, 2)}, length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.show()


def smaller_threat():
    plt.figure(figsize=(10, 7))
    plt.suptitle('scenario 3: smaller threat', fontsize=22, y=0.95)
    source = Coord(0, 5)
    target = Coord(30, 5)
    threat1 = Threat(center=Coord(10, 4), radius=4.5)
    threat2 = Threat(center=Coord(21, 4), radius=3)
    risk_limits = [1, 5, 10, 15]

    plt.subplot(2, 1, 2)
    plt.grid(True)

    lengths = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = multiple_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    y_limit = [25, 35]
    plt.ylim(y_limit)
    rad_prop = threat1.radius / (threat1.radius + threat2.radius)
    plt.plot([rad_prop, rad_prop], y_limit, color='black', linestyle='--', label='radius prop.')
    plt.legend()

    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    for risk_limit in risk_limits:
        ib = min(range(len(bs)), key=lambda i: lengths[risk_limit][i])
        b = bs[ib]
        path, length, risk = multiple_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                                 risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'risk {round(risk, 2)}, length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.show()


def non_symmetric_but_same_side():
    plt.figure(figsize=(10, 7))
    plt.suptitle('scenario 4: non symmetric threats on same s-t side', fontsize=22, y=0.95)
    source = Coord(0, 5)
    target = Coord(30, 5)
    threat1 = Threat(center=Coord(10, 4.9), radius=4.5)
    threat2 = Threat(center=Coord(20, 3), radius=4.5)
    risk_limits = [1, 5, 10, 15]

    plt.subplot(2, 1, 2)
    plt.grid(True)

    lengths = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = multiple_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    y_limit = [25, 35]
    plt.ylim(y_limit)
    rad_prop = threat1.radius / (threat1.radius + threat2.radius)
    plt.plot([rad_prop, rad_prop], y_limit, color='black', linestyle='--', label='radius prop.')
    plt.legend()

    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    for risk_limit in risk_limits:
        ib = min(range(len(bs)), key=lambda i: lengths[risk_limit][i])
        b = bs[ib]
        path, length, risk = multiple_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                                 risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'risk {round(risk, 2)}, length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.show()


def non_symmetric_other_side():
    plt.figure(figsize=(10, 7))
    plt.suptitle('scenario 5: non symmetric threats on different s-t side', fontsize=22, y=0.95)
    source = Coord(0, 5)
    target = Coord(30, 5)
    threat1 = Threat(center=Coord(10, 4), radius=4.5)
    threat2 = Threat(center=Coord(20, 7), radius=4.5)
    risk_limits = [1, 5, 10, 15]

    plt.subplot(2, 1, 2)
    plt.grid(True)

    lengths = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = multiple_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    y_limit = [25, 35]
    plt.ylim(y_limit)
    rad_prop = threat1.radius / (threat1.radius + threat2.radius)
    plt.plot([rad_prop, rad_prop], y_limit, color='black', linestyle='--', label='radius prop.')
    plt.legend()

    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    for risk_limit in risk_limits:
        ib = min(range(len(bs)), key=lambda i: lengths[risk_limit][i])
        b = bs[ib]
        path, length, risk = multiple_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                                 risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'risk {round(risk, 2)}, length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.show()


if __name__ == '__main__':
    # one_threat_under_risk_budget()
    # one_threat_under_length_budget()
    # two_symmetric_threats()
    same_threats_farther_source()
    # smaller_threat()
    # non_symmetric_but_same_side()
    # non_symmetric_other_side()
