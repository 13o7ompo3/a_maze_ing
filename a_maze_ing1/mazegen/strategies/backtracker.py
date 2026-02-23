from sys import setrecursionlimit
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

    setrecursionlimit(10000)
    def apply(self, x=0, y=0):
        self.visited.add((x, y))
        neighbours = [((x - 1, y), 8, 2),
                      ((x + 1, y), 2, 8),
                      ((x, y - 1), 1, 4),
                      ((x, y + 1), 4, 1)]
        self.rng.shuffle(neighbours)

        for c, wall, opp_wall in neighbours:
            nx, ny = c
            if nx < 0 or nx >= self.grid.width or\
               ny < 0 or ny >= self.grid.height:
                continue
            if (c not in self.visited.union(self.cells_42)):
                self.grid.remove_wall(x, y, wall)
                self.grid.remove_wall(nx, ny, opp_wall)
                sleep(0.04)
                self.viz.render()

                self.apply(nx, ny)
        self.rng.shuffle(neighbours)
        for c, wall, opp_wall in neighbours:
            nx, ny = c
            if nx < 0 or nx >= self.grid.width or\
               ny < 0 or ny >= self.grid.height:
                continue
            if (c not in self.cells_42):
                if (self.rng.random() < 0.1):
                    self.grid.remove_wall(x, y, wall)
                    self.grid.remove_wall(nx, ny, opp_wall)
                break



            
