from time import sleep
from mazegen.strategies.base import GenerationStrategy
from mazegen.grid import Grid
from random import Random
from mazegen.visualizer import ConsoleVisualizer


class RecursiveBacktracker(GenerationStrategy):
    """Implement the Recursive Backtracker algorithm for maze generation.

    Inherits from GenerationStrategy and uses a randomized depth-first search
    (DFS) approach to carve out paths, avoiding cells defined in the
    exclusion shape.
    """

    def __init__(self, grid: Grid, rng: Random,
                 viz: ConsoleVisualizer | None = None,
                 shape: set[tuple[int, int]] | None = None,
                 perfect: bool = True,
                 vizualize: bool = True):
        """Initialize the RecursiveBacktracker generation strategy.

        Args:
            grid (Grid): The maze grid object to be populated.
            rng (Random): The random number generator instance.
            viz (ConsoleVisualizer | None, optional): The visualizer object
                for rendering. Defaults to None.
            shape (set[tuple[int, int]] | None, optional): Coordinates to
                exclude from path generation. Defaults to None.
            perfect (bool, optional): Whether to generate a perfect maze
                (no loops). Defaults to True.
            vizualize (bool, optional): Whether to enable visualization.
                Defaults to True.
        """
        super().__init__(grid, rng, viz, perfect, vizualize)
        if shape is not None:
            if not isinstance(shape, set):
                raise TypeError("Expected set or None for shape, "
                                f"got {type(shape).__name__}")
            for item in shape:
                if (not isinstance(item, tuple) or len(item) != 2 or
                        not isinstance(item[0], int) or
                        not isinstance(item[1], int)):
                    raise TypeError("Expected set of tuples of two integers "
                                    "for shape")
        self.visited: set[tuple[int, int]] = set()
        self.shape: set[tuple[int, int]] | None = shape

    def apply(self, start_x: int = 0, start_y: int = 0) -> None:
        """Apply the recursive backtracker algorithm to generate the maze.

        Uses a stack to iteratively carve paths through the grid. At each step,
        it selects a random unvisited neighbor, removes the wall between them,
        and pushes the new cell onto the stack. If no unvisited neighbors are
        available, it backtracks by popping the stack. If an imperfect maze is
        requested, it subsequently removes additional walls to create loops.

        Args:
            start_x (int, optional): The starting x-coordinate for
                generation. Defaults to 0.
            start_y (int, optional): The starting y-coordinate for
                generation. Defaults to 0.
        """
        if not isinstance(start_x, int):
            raise TypeError("Expected int for start_x, "
                            f"got {type(start_x).__name__}")
        if not isinstance(start_y, int):
            raise TypeError("Expected int for start_y, "
                            f"got {type(start_y).__name__}")
        if start_x < 0 or start_y < 0:
            raise ValueError("Coordinates start_x and start_y cannot "
                             "be negative")

        stack = [(start_x, start_y)]
        self.visited.add((start_x, start_y))

        while stack:
            x, y = stack[-1]

            neighbours = [((x - 1, y), 8, 2), ((x + 1, y), 2, 8),
                          ((x, y - 1), 1, 4), ((x, y + 1), 4, 1)]
            self.rng.shuffle(neighbours)

            for c, wall, opp_wall in neighbours:
                nx, ny = c

                # If valid and unvisited...
                if (0 <= nx < self.grid.width and 0 <= ny < self.grid.height
                   and c not in self.visited and
                   ((c not in self.shape) if self.shape else True)):

                    self.grid.remove_wall(x, y, wall)
                    self.grid.remove_wall(nx, ny, opp_wall)
                    self.visited.add(c)
                    stack.append(c)

                    if self.viz and self.vizualize:
                        sleep(0.04)
                        self.viz.render_cells(x, y)
                        self.viz.render_cells(nx, ny)

                    break
            else:
                stack.pop()

        if not self.perfect:
            w, h = self.grid.width, self.grid.height
            rejected_edges = []

            for y in range(h):
                for x in range(w):
                    if self.shape and (x, y) in self.shape:
                        continue
                    if x < w - 1 and (not self.shape or
                                      (x + 1, y) not in self.shape):
                        if self.grid.get_value(x, y) & 2:
                            rejected_edges.append(((x, y), (x + 1, y), 2, 8))
                    if y < h - 1 and (not self.shape or
                                      (x, y + 1) not in self.shape):
                        if self.grid.get_value(x, y) & 4:
                            rejected_edges.append(((x, y), (x, y + 1), 4, 1))

            self.imperfect_maze(rejected_edges)
