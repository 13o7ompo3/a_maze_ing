from mazegen.grid import Grid
from mazegen.strategies.bfs_solver import BFSSolver
from mazegen.strategies.dfs_solver import DFSSolver
from mazegen.visualizer import ConsoleVisualizer


class MazeSolver:
    def __init__(self, grid: Grid, viz: ConsoleVisualizer):
        self.grid = grid
        self.viz = viz

    def solve(self, entry: tuple, exit: tuple, strategy: str) -> str:
        statigies = {
            "bfs": BFSSolver,
            "dfs": DFSSolver
        }
        if strategy not in statigies:
            raise ValueError(f"Unknown strategy: {strategy}")
        strategy_class = statigies[strategy]
        solver = strategy_class(self.grid, entry, exit, self.viz)
        return solver.solve()
