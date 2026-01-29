from abc import ABC, abstractmethod
from random import Random
from mazegen.grid import Grid
from mazegen.visualizer import ConsoleVisualizer


class GenerationStrategy(ABC):
    def __init__(self, grid: Grid, rng: Random, cells_42: set,
                 viz: ConsoleVisualizer):
        self.grid = grid
        self.rng = rng
        self.cells_42 = cells_42
        self.viz = viz

    @abstractmethod
    def apply(self):
        pass
