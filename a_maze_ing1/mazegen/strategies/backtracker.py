from time import sleep
from mazegen.strategies.base import GenerationStrategy
from mazegen.grid import Grid
from random import Random
from mazegen.visualizer import ConsoleVisualizer


class RecursiveBacktracker(GenerationStrategy):
    def __init__(self, grid: Grid, rng: Random, cells_42: set,
                 viz: ConsoleVisualizer):
        super().__init__(grid, rng, cells_42, viz)
        self.visited = set()

    def apply(self, x=0, y=0):
        self.visited.add((x, y))
        neighbours = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        self.rng.shuffle(neighbours)
        for c in neighbours:
            nx, ny = c
            if nx < 0 or nx >= self.grid.width or\
               ny < 0 or ny >= self.grid.height:
                continue
            if c not in self.visited.union(self.cells_42):
                if nx == x - 1:
                    wall = 8
                    opp_wall = 2
                elif nx == x + 1:
                    wall = 2
                    opp_wall = 8
                elif ny == y - 1:
                    wall = 1
                    opp_wall = 4
                elif ny == y + 1:
                    wall = 4
                    opp_wall = 1

                self.grid.remove_wall(x, y, wall)
                self.grid.remove_wall(nx, ny, opp_wall)
                sleep(0.01)
                self.viz.render()

                self.apply(nx, ny)
