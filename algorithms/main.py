from algorithms.planning import single_threat_shortest_path_with_risk_constraint, \
    two_threats_shortest_path_with_risk_constraint
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
    legend_font = 10
    source = Coord(0,1)
    target = Coord(1000,0)
    radius = 150

    plt.figure(figsize=(10, 8))

    plt.suptitle('scenario 1: two symmetric threats', fontsize=22, y=0.98)

    threat1_center = Coord(250,0)
    threat2_center = Coord(1000-250,0)
    risk_limit = 2 * radius

    threat1 = Threat(center=threat1_center, radius=radius)
    threat2 = Threat(center=threat2_center, radius=radius)

    # find all results
    lengths = {}
    cases = {}
    bs = np.arange(0, 1.01, 0.125)

    # plot shortest path in the environment
    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.ylim([-200,200])
    plt.ylabel('shortest path under budget and partition')

    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    for b in bs:
        path, length, risk, cs = two_threats_shortest_path_with_risk_constraint(
            source, target, [threat1, threat2], risk_limit, budgets=[b, 1 - b])
        lengths[b] = length
        cases[b] = cs
        if b <= 0.5:
            plt.plot([p.x for p in path], [p.y for p in path],
                     label=f'length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=legend_font)

    # plot length as function of budget partition
    plt.subplot(2, 1, 2)
    plt.grid(True)

    plt.plot(bs, [lengths[b] for b in bs], label=f'risk limit {risk_limit}')
    plt.scatter(bs, [lengths[b] for b in bs], color=plt.gca().lines[-1].get_color())
    for b in bs:
        plt.text(b, lengths[b], f'{cases[b][0]},{cases[b][1]}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    plt.ylim([min([lengths[b] for b in bs]), max([lengths[b] for b in bs])])
    plt.legend(fontsize=legend_font)

    plt.savefig(f'../plots/scenario 1 - two symmetric threats in different locations.png')


def two_symmetric_threats_zoom_in():
    legend_font = 10
    source = Coord(0,1)
    target = Coord(1000,0)
    radius = 150

    plt.figure(figsize=(20, 8))

    plt.suptitle('scenario 1: two symmetric threats', fontsize=22, y=0.98)

    threat1_center = Coord(250,0)
    threat2_center = Coord(1000-250,0)

    threat1 = Threat(center=threat1_center, radius=radius)
    threat2 = Threat(center=threat2_center, radius=radius)

    low_risk_limits = [350, 375, 400, 425, 450, 475, 500]
    high_risk_limits = [450, 475, 500, 525, 550, 575, 600]

    # plot shortest path in the environment
    plt.subplot(2, 2, 1)
    plt.grid(True)
    plt.ylim([-200,200])
    plt.ylabel('shortest path under budget')

    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    # find all results
    lengths = {}
    cases = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in low_risk_limits:
            path, length, risk, cs = two_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]
            cases[risk_limit] = [cs] if risk_limit not in cases else cases[risk_limit] + [cs]

    for risk_limit in low_risk_limits:
        ib = min(range(len(bs)), key=lambda i: lengths[risk_limit][i])
        b = bs[ib]
        path, length, risk, _ = two_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                               risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=legend_font)

    # plot length as function of budget partition
    plt.subplot(2, 2, 3)
    plt.grid(True)
    for risk_limit in low_risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')
        plt.scatter(bs, lengths[risk_limit], color=plt.gca().lines[-1].get_color())
        for x, y, cs in zip(bs, lengths[risk_limit], cases[risk_limit]):
            plt.text(x, y, f'{cs[0]},{cs[1]}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    plt.ylim([min(lengths[low_risk_limits[-1]]), max(lengths[low_risk_limits[0]])])
    plt.legend(fontsize=legend_font)

    # plot shortest path in the environment
    plt.subplot(2, 2, 2)
    plt.grid(True)
    plt.ylim([-200, 200])

    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    # find all results
    lengths = {}
    cases = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in high_risk_limits:
            path, length, risk, cs = two_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]
            cases[risk_limit] = [cs] if risk_limit not in cases else cases[risk_limit] + [cs]

    for risk_limit in high_risk_limits:
        ib = min(range(len(bs)), key=lambda i: lengths[risk_limit][i])
        b = bs[ib]
        path, length, risk, _ = two_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                               risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=legend_font)

    # plot length as function of budget partition
    plt.subplot(2, 2, 4)
    plt.grid(True)
    for risk_limit in high_risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')
        plt.scatter(bs, lengths[risk_limit], color=plt.gca().lines[-1].get_color())
        for x, y, cs in zip(bs, lengths[risk_limit], cases[risk_limit]):
            plt.text(x, y, f'{cs[0]},{cs[1]}')

    plt.xlabel('% budget to first threat')
    plt.xlim([0, 1])
    plt.ylim([min(lengths[high_risk_limits[-1]]), max(lengths[high_risk_limits[0]])])
    plt.legend(fontsize=legend_font)

    plt.savefig(f'../plots/scenario 1 - two symmetric threats zoom in.png')


def same_threats_farther_source():
    plt.figure(figsize=(10, 7))
    title = 'scenario 2: farther source'
    plt.suptitle('scenario 2: farther source', fontsize=22, y=0.98)
    source = Coord(-600, 1)
    target = Coord(1000, 1)
    radius = 100
    threat1 = Threat(center=Coord(300, 0), radius=radius)
    threat2 = Threat(center=Coord(700, 0), radius=radius)
    risk_limits = [0.5 * radius, radius, 1.5 * radius, 2 * radius, 2.5 * radius,
                   3 * radius, 3.5 * radius, 3.9 * radius, 4 * radius]

    plt.subplot(2, 1, 2)
    plt.grid(True)
    plt.title('shortest paths')

    lengths = {}
    cases = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk, cs = two_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]
            cases[risk_limit] = [cs] if risk_limit not in cases else cases[risk_limit] + [cs]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')
        plt.scatter(bs, lengths[risk_limit], color=plt.gca().lines[-1].get_color())
        for x, y, cs in zip(bs, lengths[risk_limit], cases[risk_limit]):
            plt.text(x, y, f'{cs[0]},{cs[1]}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    plt.ylim([min(lengths[risk_limits[-1]]), max(lengths[risk_limits[0]])])
    plt.legend(fontsize=12)

    plt.subplot(2, 1, 1)
    plt.grid(True)
    plt.title('path length as function of first threat budget')
    plt.scatter([source.x, target.x], [source.y, target.y])
    plt.plot([p.x for p in threat1.boundary], [p.y for p in threat1.boundary], color='blue')
    plt.plot([p.x for p in threat2.boundary], [p.y for p in threat2.boundary], color='blue')

    for risk_limit in risk_limits:
        ib = min(range(len(bs)), key=lambda i: lengths[risk_limit][i])
        b = bs[ib]
        path, length, risk, _ = two_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                            risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.ylim(-175, 175)
    plt.savefig(f'../plots/{title}.png')


def bigger_threat():
    plt.figure(figsize=(10, 7))
    title = 'scenario 3: bigger threat'
    plt.suptitle(title, fontsize=22, y=0.98)
    source = Coord(0, 1)
    target = Coord(1000, 1)
    radius = 100
    threat1 = Threat(center=Coord(300, 0), radius=1.3 * radius)
    threat2 = Threat(center=Coord(700, 0), radius=radius)
    risk_limits = [0.5 * radius, radius, 1.5 * radius, 2 * radius, 2.25 * radius, 2.5 * radius, 2.75 * radius,
                   3 * radius]

    plt.subplot(2, 1, 2)
    plt.grid(True)
    plt.title('shortest paths')

    lengths = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = two_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    y_limit = [1000, 1050]
    plt.ylim(y_limit)
    rad_prop = threat1.radius / (threat1.radius + threat2.radius)
    plt.plot([rad_prop, rad_prop], y_limit, color='black', linestyle='--', label='radius prop.')
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
        path, length, risk, _ = two_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                               risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.savefig(f'../plots/{title}.png')


def asymmetric_but_same_side():
    plt.figure(figsize=(10, 7))
    title = 'scenario 4: non symmetric threats on same s-t side'
    plt.suptitle(title, fontsize=22, y=0.98)
    source = Coord(0, 1)
    target = Coord(1000, 1)
    radius = 100
    threat1 = Threat(center=Coord(300, 0), radius=radius)
    threat2 = Threat(center=Coord(700, -50), radius=radius)
    risk_limits = [0.5 * radius, radius, 1.5 * radius, 2 * radius, 2.25 * radius, 2.5 * radius, 2.75 * radius,
                   3 * radius]

    plt.subplot(2, 1, 2)
    plt.grid(True)
    plt.title('shortest paths')

    lengths = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = two_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    y_limit = [1000, 1050]
    plt.ylim(y_limit)
    rad_prop = threat1.radius / (threat1.radius + threat2.radius)
    plt.plot([rad_prop, rad_prop], y_limit, color='black', linestyle='--', label='radius prop.')
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
        path, length, risk = two_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                            risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.savefig(f'../plots/{title}.png')


def asymmetric_other_side():
    plt.figure(figsize=(10, 7))
    title = 'scenario 5: non symmetric threats on different s-t side'
    plt.suptitle(title, fontsize=22, y=0.98)
    source = Coord(0, 1)
    target = Coord(1000, 1)
    radius = 100
    threat1 = Threat(center=Coord(300, 51), radius=radius)
    threat2 = Threat(center=Coord(700, -49), radius=radius)
    risk_limits = [0.5 * radius, radius, 1.5 * radius, 2 * radius, 2.25 * radius, 2.5 * radius, 2.75 * radius,
                   3 * radius]

    plt.subplot(2, 1, 2)
    plt.grid(True)
    plt.title('shortest paths')

    lengths = {}
    bs = np.arange(0, 1.01, 0.05)
    for b in bs:
        budgets = [b, 1 - b]

        for risk_limit in risk_limits:
            path, length, risk = two_threats_shortest_path_with_risk_constraint(
                source, target, [threat1, threat2], risk_limit, budgets)

            lengths[risk_limit] = [length] if risk_limit not in lengths else lengths[risk_limit] + [length]

    for risk_limit in risk_limits:
        plt.plot(bs, lengths[risk_limit], label=f'risk limit {risk_limit}')

    plt.xlabel('% budget to first threat')
    plt.ylabel('distance')
    plt.xlim([0, 1])
    y_limit = [1000, 1050]
    plt.ylim(y_limit)
    rad_prop = threat1.radius / (threat1.radius + threat2.radius)
    plt.plot([rad_prop, rad_prop], y_limit, color='black', linestyle='--', label='radius prop.')
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
        path, length, risk = two_threats_shortest_path_with_risk_constraint(source, target, [threat1, threat2],
                                                                            risk_limit, budgets=[b, 1 - b])
        plt.plot([p.x for p in path], [p.y for p in path],
                 label=f'length {round(length, 2)}, budgets part. {round(b, 2)},{round(1 - b, 2)}')

    plt.legend(fontsize=12)

    plt.savefig(f'../plots/{title}.png')


if __name__ == '__main__':
    # one_threat_under_risk_budget()
    # one_threat_under_length_budget()
    two_symmetric_threats()
    # two_symmetric_threats_zoom_in()
    # same_threats_farther_source()
    # bigger_threat()
    # asymmetric_but_same_side()
    # asymmetric_other_side()
