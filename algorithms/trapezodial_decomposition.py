from typing import List

import shapely.ops

from geometry.polygon import Polygon

import matplotlib.pyplot as plt

from shapely.geometry import Polygon


def trapezoidal_decomposition(environment, obstacles):
    # Ensure the environment is a Shapely Polygon
    if not isinstance(environment, Polygon):
        raise ValueError("The environment must be a Shapely Polygon.")

    trapezoids = [environment]

    for obstacle in obstacles:
        # Ensure all obstacles are Shapely Polygons
        if not isinstance(obstacle, Polygon):
            raise ValueError("All obstacles must be Shapely Polygons.")

        new_trapezoids = []

        # Decompose each trapezoid using the obstacle
        for trapezoid in trapezoids:
            intersection = trapezoid.intersection(obstacle)

            if not intersection.is_empty:
                # Triangulate the intersection polygon
                triangles = shapely.ops.triangulate(intersection)

                # Add non-empty triangles to the new trapezoids list
                new_trapezoids.extend([Polygon(triangle) for triangle in triangles])

            # Add the difference between the trapezoid and the obstacle
            difference = trapezoid.difference(obstacle)
            if not difference.is_empty:
                new_trapezoids.extend([Polygon(difference)])

        trapezoids = new_trapezoids

    return trapezoids


# Example usage:
if __name__ == "__main__":
    # Define the environment as a Shapely rectangle
    environment = Polygon([(0, 0), (10, 0), (10, 6), (0, 6)])

    # Define a list of obstacle polygons
    obstacles = [
        Polygon([(2, 2), (4, 2), (4, 4), (2, 4)]),
        Polygon([(6, 1), (8, 1), (8, 5), (6, 5)])
    ]

    for o in obstacles:
        plt.plot(*o.exterior.xy)
    # plt.show()

    # Get the trapezoidal decomposition of the environment with obstacles
    result = trapezoidal_decomposition(environment, obstacles)

    # Print the trapezoids (Polygons)
    for i, trapezoid in enumerate(result, start=1):
        print(f"Trapezoid {i}: {trapezoid}")
        plt.plot(*trapezoid.exterior.xy)
    plt.show()
