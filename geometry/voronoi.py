import itertools
from typing import List, Dict

import numpy as np
import shapely
from matplotlib import pyplot as plot
from matplotlib.collections import LineCollection
from scipy.spatial import ConvexHull, Voronoi
from shapely import ops

from geometry.circle import Circle
from geometry.coord import Coord
from geometry.polygon import Polygon

# --- Misc. geometry code -----------------------------------------------------

'''
Pick N points uniformly from the unit disc
This sampling algorithm does not use rejection sampling.
'''


def disc_uniform_pick(N):
    angle = (2 * np.pi) * np.random.random(N)
    out = np.stack([np.cos(angle), np.sin(angle)], axis=1)
    out *= np.sqrt(np.random.random(N))[:, None]
    return out


def norm2(X):
    return np.sqrt(np.sum(X ** 2))


def normalized(X):
    return X / norm2(X)


# --- Delaunay triangulation --------------------------------------------------

def get_triangle_normal(A, B, C):
    return normalized(np.cross(A, B) + np.cross(B, C) + np.cross(C, A))


def get_power_circumcenter(A, B, C):
    N = get_triangle_normal(A, B, C)
    return (-.5 / N[2]) * N[:2]


def is_ccw_triangle(A, B, C):
    M = np.concatenate([np.stack([A, B, C]), np.ones((3, 1))], axis=1)
    return np.linalg.det(M) > 0


def get_power_triangulation(S, R):
    # Compute the lifted weighted points
    S_norm = np.sum(S ** 2, axis=1) - R ** 2
    S_lifted = np.concatenate([S, S_norm[:, None]], axis=1)

    # Special case for 3 points
    if S.shape[0] == 3:
        if is_ccw_triangle(S[0], S[1], S[2]):
            return [[0, 1, 2]], np.array([get_power_circumcenter(*S_lifted)])
        else:
            return [[0, 2, 1]], np.array([get_power_circumcenter(*S_lifted)])

    # Compute the convex hull of the lifted weighted points
    hull = ConvexHull(S_lifted)

    # Extract the Delaunay triangulation from the lower hull
    tri_list = tuple([a, b, c] if is_ccw_triangle(S[a], S[b], S[c]) else [a, c, b] for (a, b, c), eq in
                     zip(hull.simplices, hull.equations) if eq[2] <= 0)

    # Compute the Voronoi points
    V = np.array([get_power_circumcenter(*S_lifted[tri]) for tri in tri_list])

    # Job done
    return tri_list, V


# --- Compute Voronoi cells ---------------------------------------------------

'''
Compute the segments and half-lines that delimits each Voronoi cell
  * The segments are oriented so that they are in CCW order
  * Each cell is a list of (i, j), (A, U, tmin, tmax) where
     * i, j are the indices of two ends of the segment. Segments end points are
       the circumcenters. If i or j is set to None, then it's an infinite end
     * A is the origin of the segment
     * U is the direction of the segment, as a unit vector
     * tmin is the parameter for the left end of the segment. Can be -1, for minus infinity
     * tmax is the parameter for the right end of the segment. Can be -1, for infinity
     * Therefore, the endpoints are [A + tmin * U, A + tmax * U]
'''


def get_voronoi_cells(S, V, tri_list):
    # Keep track of which circles are included in the triangulation
    vertices_set = frozenset(itertools.chain(*tri_list))

    # Keep track of which edge separate which triangles
    edge_map = {}
    for i, tri in enumerate(tri_list):
        for edge in itertools.combinations(tri, 2):
            edge = tuple(sorted(edge))
            if edge in edge_map:
                edge_map[edge].append(i)
            else:
                edge_map[edge] = [i]

    # For each triangle
    voronoi_cell_map = {i: [] for i in vertices_set}

    for i, (a, b, c) in enumerate(tri_list):
        # For each edge of the triangle
        for u, v, w in ((a, b, c), (b, c, a), (c, a, b)):
            # Finite Voronoi edge
            edge = tuple(sorted((u, v)))
            if len(edge_map[edge]) == 2:
                j, k = edge_map[edge]
                if k == i:
                    j, k = k, j

                # Compute the segment parameters
                U = V[k] - V[j]
                U_norm = norm2(U)

                # Add the segment
                voronoi_cell_map[u].append(((j, k), (V[j], U / U_norm, 0, U_norm)))
            else:
                # Infinite Voronoi edge
                # Compute the segment parameters
                A, B, C, D = S[u], S[v], S[w], V[i]
                U = normalized(B - A)
                I = A + np.dot(D - A, U) * U
                W = normalized(I - D)
                if np.dot(W, I - C) < 0:
                    W = -W

                # Add the segment
                voronoi_cell_map[u].append(((edge_map[edge][0], -1), (D, W, 0, None)))
                voronoi_cell_map[v].append(((-1, edge_map[edge][0]), (D, -W, None, 0)))

    # Order the segments
    def order_segment_list(segment_list):
        # Pick the first element
        first = min((seg[0][0], i) for i, seg in enumerate(segment_list))[1]

        # In-place ordering
        segment_list[0], segment_list[first] = segment_list[first], segment_list[0]
        for i in range(len(segment_list) - 1):
            for j in range(i + 1, len(segment_list)):
                if segment_list[i][0][1] == segment_list[j][0][0]:
                    segment_list[i + 1], segment_list[j] = segment_list[j], segment_list[i + 1]
                    break

        # Job done
        return segment_list

    # Job done
    return {i: order_segment_list(segment_list) for i, segment_list in voronoi_cell_map.items()}


# --- Plot all the things -----------------------------------------------------

def display(S, R, tri_list, voronoi_cell_map):
    # Setup
    fig, ax = plot.subplots()
    plot.axis('equal')
    plot.axis('off')

    # Set min/max display size, as Matplotlib does it wrong
    min_corner = np.amin(S, axis=0) - np.max(R)
    max_corner = np.amax(S, axis=0) + np.max(R)
    plot.xlim((min_corner[0], max_corner[0]))
    plot.ylim((min_corner[1], max_corner[1]))

    # Plot the samples
    for Si, Ri in zip(S, R):
        ax.add_artist(plot.Circle(Si, Ri, fill=True, alpha=.4, lw=0., color='#8080f0', zorder=1))

    # Plot the power triangulation
    edge_set = frozenset(tuple(sorted(edge)) for tri in tri_list for edge in itertools.combinations(tri, 2))
    line_list = LineCollection([(S[i], S[j]) for i, j in edge_set], lw=1., colors='.9')
    line_list.set_zorder(0)
    ax.add_collection(line_list)

    # Plot the Voronoi cells
    edge_map = {}
    for segment_list in voronoi_cell_map.values():
        for edge, (A, U, tmin, tmax) in segment_list:
            edge = tuple(sorted(edge))
            if edge not in edge_map:
                if tmax is None:
                    tmax = 10
                if tmin is None:
                    tmin = -10

                edge_map[edge] = (A + tmin * U, A + tmax * U)

    line_list = LineCollection(edge_map.values(), lw=1., colors='k')
    line_list.set_zorder(0)
    ax.add_collection(line_list)

    # Job done
    plot.show()


# --- Main entry point --------------------------------------------------------

def voronoi_of_coords(coords: List[Coord]) -> Dict[Coord, Polygon]:
    world = Polygon([Coord(0, 0), Coord(0, 1000), Coord(1000, 1000), Coord(1000, 0)])

    np_coords = np.array([coord.xy for coord in coords])

    vor = Voronoi(points=np_coords)
    lines = [shapely.geometry.LineString(vor.vertices[line]) for line in
             vor.ridge_vertices if -1 not in line]

    polys = ops.polygonize(lines)

    return polys


if __name__ == '__main__':
    circles = [Circle(Coord(100, 100), 50), Circle(Coord(200, 300), 60), Circle(Coord(300, 60), 50),
               Circle(Coord(400, 100), 50), Circle(Coord(500, 500), 100), Circle(Coord(600, 250), 50)]
    voronoi_of_coords([c.center for c in circles])

# def voronoi_of_circles(circles: List[Circle]) -> Dict[Circle, Polygon]:
#     centers = [circle.center.xy for circle in circles]
#     radii = [circle.radius for circle in circles]
#
#     tri_list, V = get_power_triangulation([coord.xy for coord in centers], radii)
#
#     voronoi_cell_map = get_voronoi_cells(S, V, tri_list)
#
#     circles_to_polygons = {circle: None for circle in circles}
#     for circle, segments_polygons in voronoi_cell_map.items():
#         coords = []
#         for segment in segments_polygons:
#             coords.append()
#         circles_to_polygons[circle] = Polygon(coords)
#
#     return circles_to_polygons
#
# if __name__ == '__main__':
#     # Generate samples, S contains circles center, R contains circles radius
#     # sample_count = 32
#     # S = 5 * disc_uniform_pick(sample_count)
#     # R = .8 * np.random.random(sample_count) + .2
#     # S = np.array([s * 1000 for s in S])
#     # R = R * 1000
#     circles = [Circle(Coord(0,0),10), Circle(Coord(100,70),25), Circle(Coord(50,200),20)]
#     centers = np.array([np.array(circle.center.xy) for circle in circles])
#     radii = np.array([circle.radius for circle in circles])
#
#     S = centers
#     R = radii
#
#     # Compute the power triangulation of the circles
#     tri_list, V = get_power_triangulation(S, R)
#
#     # Compute the Voronoi cells
#     voronoi_cell_map = get_voronoi_cells(S, V, tri_list)
#
#     # Display the result
#     display(S, R, tri_list, voronoi_cell_map)
#
#
#
#
#
