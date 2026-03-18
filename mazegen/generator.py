from mazegen.grid import Grid
import random
from mazegen.strategies.backtracker import RecursiveBacktracker
from mazegen.strategies.kruskal import Kruskal
from mazegen.visualizer import ConsoleVisualizer
# from mazegen.strategies.prim import Prim


class MazeGenerator:
    def __init__(self, grid: Grid, width: int, height: int,
                 viz: ConsoleVisualizer, seed: str | int,
                 algorithm_name="backtracker"):
        self.width = width
        self.height = height
        self.grid = grid
        self.visited = set()
        self.imprint_42 = set()
        self.rng = random.Random(seed)
        self.algorithm_name = algorithm_name
        self.viz = viz

    def generate(self):
        self._imprint_42()
        self.viz.imprint_42 = self.imprint_42
        strategies = {
            "backtracker": RecursiveBacktracker,
            "kruskal": Kruskal,
            # "prim": Prim
        }

        if self.algorithm_name not in strategies:
            raise ValueError(f"Unknown algorithm: {self.algorithm_name}")
        strategy_class = strategies[self.algorithm_name]
        strategy = strategy_class(self.grid, self.rng, self.imprint_42,
                                  self.viz)
        self.viz.render()
        strategy.apply()

    def _imprint_42(self):
        shape = [
            "1   111",
            "1     1",
            "111 111",
            "  1 1  ",
            "  1 111"
        ]

        shape_h = len(shape)
        shape_w = len(shape[0])

        if self.width < shape_w + 2 or self.height < shape_h + 2:
            raise ValueError("Grid too small for imprinting 42")

        start_x = (self.width - shape_w) // 2
        start_y = (self.height - shape_h) // 2

        for y, row in enumerate(shape):
            for x, char in enumerate(row):
                if char == '1':
                    self.imprint_42.add((start_x + x, start_y + y))
