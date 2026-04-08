from time import sleep
from mazegen.strategies.base import GenerationStrategy
from mazegen.grid import Grid
from random import Random
from mazegen.visualizer import ConsoleVisualizer


class RecursiveBacktracker(GenerationStrategy):
    def __init__(self, grid: Grid, rng: Random,
                 viz: ConsoleVisualizer | None = None,
                 shape: set[tuple[int, int]] | None = None,
                 perfect: bool = True,
                 vizualize: bool = True):
        super().__init__(grid, rng, viz, perfect, vizualize)
        self.visited: set[tuple[int, int]] = set()
        self.shape: set[tuple[int, int]] | None = shape

    def apply(self, start_x: int = 0, start_y: int = 0) -> None:
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

            p_c = 0.05
            k = int(p_c * ((w * h) - w - h + 1))
            self.rng.shuffle(rejected_edges)

            for cell_a, cell_b, wall_a, wall_b in rejected_edges:
                if k <= 0:
                    break
                x, y = cell_a
                nx, ny = cell_b
                if not self._creates_2x2_room(x, y, nx, ny, wall_a):
                    self.grid.remove_wall(x, y, wall_a)
                    self.grid.remove_wall(nx, ny, wall_b)
                    k -= 1
                    if self.viz and self.vizualize:
                        sleep(0.04)
                        self.viz.render_cells(x, y)
                        self.viz.render_cells(nx, ny)
