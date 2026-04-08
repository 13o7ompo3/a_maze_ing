from mazegen.grid import Grid
import random
from mazegen.strategies.backtracker import RecursiveBacktracker
from mazegen.strategies.kruskal import Kruskal
from mazegen.visualizer import ConsoleVisualizer


class MazeGenerator:
    def __init__(self, grid: Grid, width: int, height: int,
                 viz: ConsoleVisualizer | None = None, seed: str | None = None,
                 algorithm_name: str = "backtracker",
                 shape: set[tuple[int, int]] | None = None,
                 perfect: bool = True, vizualize: bool = True):
        self.width = width
        self.height = height
        self.grid = grid
        self.shape: set[tuple[int, int]] | None = shape
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self.algorithm_name = algorithm_name
        self.viz = viz
        self.perfect = perfect
        self.vizualize = vizualize

    def generate(self) -> None:
        if self.viz:
            self.viz.imprint_42 = self.shape if self.shape else set()
        strategies = {
            "backtracker": RecursiveBacktracker,
            "kruskal": Kruskal,
        }

        if self.algorithm_name not in strategies:
            raise ValueError(f"Unknown algorithm: {self.algorithm_name}")
        strategy_class = strategies[self.algorithm_name]
        strategy = strategy_class(self.grid, self.rng, self.viz, self.shape,
                                  self.perfect, self.vizualize)
        if self.viz:
            self.viz.render()
        strategy.apply()
