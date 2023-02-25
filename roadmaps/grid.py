from roadmap.roadmap import Roadmap

from environment.environment import Environment
from geometry.coord import Coord

GRID_STEP = 50


class Grid(Roadmap):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        grid_nodes = []
        for x in range(0, int(environment.x_range), GRID_STEP):
            row = []
            for y in range(0, int(environment.y_range), GRID_STEP):
                row.append(Coord(x,y))

            grid_nodes.append(row)

        grid_edges = []
        for r in range(1, len(grid_nodes)-1):
            for c in range(1, len(grid_nodes[0])-1):
                grid_edges.append((grid_nodes[r][c], grid_nodes[r][c+1]))
                grid_edges.append((grid_nodes[r][c], grid_nodes[r][c-1]))

                grid_edges.append((grid_nodes[r][c], grid_nodes[r+1][c]))
                grid_edges.append((grid_nodes[r][c], grid_nodes[r+1][c-1]))
                grid_edges.append((grid_nodes[r][c], grid_nodes[r+1][c+1]))

                grid_edges.append((grid_nodes[r][c], grid_nodes[r-1][c]))
                grid_edges.append((grid_nodes[r][c], grid_nodes[r-1][c-1]))
                grid_edges.append((grid_nodes[r][c], grid_nodes[r-1][c+1]))

                grid_edges.append((grid_nodes[r][c], grid_nodes[r - 1][c]))
                grid_edges.append((grid_nodes[r][c], grid_nodes[r - 1][c - 1]))
                grid_edges.append((grid_nodes[r][c], grid_nodes[r - 1][c + 1]))

        self._add_edges(grid_edges)
