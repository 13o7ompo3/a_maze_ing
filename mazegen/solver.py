from mazegen.grid import Grid
from mazegen.strategies.bfs_solver import BFSSolver
from mazegen.strategies.dfs_solver import DFSSolver
from mazegen.visualizer import ConsoleVisualizer


class MazeSolver:
    def __init__(self, grid: Grid, entry: tuple, exit: tuple,
                 viz: ConsoleVisualizer | None = None,
                 strategy: str = "bfs",
                 vizualize: bool = True) -> None:
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.viz = viz
        self.strategy = strategy
        self.vizualize = vizualize

    def solve(self) -> str:
        statigies = {
            "bfs": BFSSolver,
            "dfs": DFSSolver
        }
        if self.strategy not in statigies:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        strategy_class = statigies[self.strategy]
        solver = strategy_class(self.grid, self.entry, self.exit, self.viz,
                                self.vizualize)
        return solver.solve()
