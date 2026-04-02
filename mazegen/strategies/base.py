from abc import ABC, abstractmethod
from random import Random
from mazegen.grid import Grid
from mazegen.visualizer import ConsoleVisualizer


class GenerationStrategy(ABC):
    def __init__(self, grid: Grid, rng: Random, cells_42: set,
                 viz: ConsoleVisualizer = None, perfect: bool = True,
                 vizualize: bool = True):
        self.grid = grid
        self.rng = rng
        self.cells_42 = cells_42
        self.viz = viz
        self.perfect = perfect
        self.vizualize = vizualize

    @abstractmethod
    def apply(self):
        pass


class SolverStrategy(ABC):
    def __init__(self, grid: Grid, entry: tuple, exit: tuple,
                 viz: ConsoleVisualizer = None,
                 vizualize: bool = True) -> None:
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.viz = viz
        self.vizualize = vizualize

    @abstractmethod
    def solve(self) -> str:
        pass
