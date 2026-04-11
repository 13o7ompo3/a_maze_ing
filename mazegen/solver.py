from mazegen.grid import Grid
from mazegen.strategies.bfs_solver import BFSSolver
from mazegen.strategies.dfs_solver import DFSSolver
from mazegen.visualizer import ConsoleVisualizer


class MazeSolver:
    """Manage the execution of maze solving strategies.

    This class acts as a context or factory that selects and executes a
    specific maze-solving strategy (e.g., Breadth-First Search or
    Depth-First Search) based on the provided configuration.
    """

    def __init__(self, grid: Grid, entry: tuple[int, int],
                 exit: tuple[int, int],
                 viz: ConsoleVisualizer | None = None,
                 strategy: str = "bfs",
                 vizualize: bool = True) -> None:
        """Initialize the MazeSolver with grid, endpoints, and strategy.

        Args:
            grid (Grid): The maze grid object to be solved.
            entry (tuple): The (x, y) coordinate pair for the maze entry.
            exit (tuple): The (x, y) coordinate pair for the maze exit.
            viz (ConsoleVisualizer | None, optional): The visualizer object
                for rendering the solving process. Defaults to None.
            strategy (str, optional): The name of the solving strategy to
                use ('bfs' or 'dfs'). Defaults to "bfs".
            vizualize (bool, optional): Whether to enable visualization
                during solving. Defaults to True.
        """
        if not isinstance(grid, Grid):
            raise TypeError("Expected Grid for grid, "
                            f"got {type(grid).__name__}")
        if not isinstance(entry, tuple):
            raise TypeError("Expected tuple for entry, "
                            f"got {type(entry).__name__}")
        if not isinstance(exit, tuple):
            raise TypeError("Expected tuple for exit, "
                            f"got {type(exit).__name__}")
        if viz is not None and not isinstance(viz, ConsoleVisualizer):
            raise TypeError("Expected ConsoleVisualizer or None for viz, "
                            f"got {type(viz).__name__}")
        if not isinstance(strategy, str):
            raise TypeError("Expected str for strategy, "
                            f"got {type(strategy).__name__}")
        if not strategy.strip():
            raise ValueError("strategy cannot be an empty string")
        if not isinstance(vizualize, bool):
            raise TypeError("Expected bool for vizualize, "
                            f"got {type(vizualize).__name__}")
        if (len(entry) != 2 or not isinstance(entry[0], int) or
                not isinstance(entry[1], int)):
            raise ValueError("entry must be a tuple of two integers")
        if (len(exit) != 2 or not isinstance(exit[0], int) or
                not isinstance(exit[1], int)):
            raise ValueError("exit must be a tuple of two integers")
        if entry[0] < 0 or entry[1] < 0:
            raise ValueError("entry coordinates cannot be negative")
        if exit[0] < 0 or exit[1] < 0:
            raise ValueError("exit coordinates cannot be negative")
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.viz = viz
        self.strategy = strategy
        self.vizualize = vizualize

    def solve(self) -> str:
        """Execute the selected maze solving strategy.

        Instantiates the appropriate solver class based on the chosen strategy
        and triggers its solving algorithm.

        Returns:
            str: A string of directional characters ('N', 'S', 'E', 'W')
                representing the path from entry to exit.

        Raises:
            ValueError: If the specified strategy is not a registered
                solver strategy.
        """
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
