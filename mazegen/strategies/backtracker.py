from time import sleep
from mazegen.strategies.base import GenerationStrategy
from mazegen.grid import Grid
from random import Random
from mazegen.visualizer import ConsoleVisualizer


class RecursiveBacktracker(GenerationStrategy):
    def __init__(self, grid: Grid, rng: Random, cells_42: set,
                 viz: ConsoleVisualizer = None, perfect: bool = True,
                 vizualize: bool = True):
        super().__init__(grid, rng, cells_42, viz, perfect, vizualize)
        self.visited = set()

    def apply(self, start_x=0, start_y=0):
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
                   and c not in self.visited and c not in self.cells_42):

                    self.grid.remove_wall(x, y, wall)
                    self.grid.remove_wall(nx, ny, opp_wall)
                    self.visited.add(c)
                    stack.append(c)

                    if self.viz and self.vizualize:
                        sleep(0.04)
                        self.viz.render_cells(x, y)
                        self.viz.render_cells(nx, ny)

                    break  # We found a path! Break out of the for-loop.

            else:
                stack.pop()  # Dead end hit, remove from stack

                if not self.perfect:
                    for c, wall, opp_wall in neighbours:
                        nx, ny = c
                        if (0 <= nx < self.grid.width
                            and 0 <= ny < self.grid.height
                           and c not in self.cells_42):

                            if self.rng.random() < 0.1:
                                self.grid.remove_wall(x, y, wall)
                                self.grid.remove_wall(nx, ny, opp_wall)
                                if self.viz and self.vizualize:
                                    sleep(0.04)
                                    self.viz.render_cells(x, y)
                                    self.viz.render_cells(nx, ny)
                                break

        if self.viz and self.vizualize:
            self.viz.render()
