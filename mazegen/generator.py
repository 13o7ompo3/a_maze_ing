from mazegen.grid import Grid
import random
from mazegen.strategies.backtracker import RecursiveBacktracker
from mazegen.strategies.kruskal import Kruskal
from mazegen.visualizer import ConsoleVisualizer


class MazeGenerator:
    """Manage the generation of mazes using specified algorithms.

    This class acts as a coordinator to initialize the maze grid and apply the
    chosen generation strategy (e.g., Recursive Backtracker or
    Kruskal's algorithm).
    """

    def __init__(self, grid: Grid, width: int, height: int,
                 viz: ConsoleVisualizer | None = None,
                 seed: str | None = None,
                 algorithm_name: str = "backtracker",
                 shape: set[tuple[int, int]] | None = None,
                 perfect: bool = True, vizualize: bool = True):
        """Initialize the MazeGenerator with grid, dimensions, and config.

        Args:
            grid (Grid): The maze grid object to be populated.
            width (int): The total width (number of columns) of the grid.
            height (int): The total height (number of rows) of the grid.
            viz (ConsoleVisualizer | None, optional): The visualizer object
                for rendering the generation process. Defaults to None.
            seed (str | int | None, optional): The seed for the random number
                generator to ensure reproducibility. Defaults to None.
            algorithm_name (str, optional): The name of the generation
                algorithm to use ('backtracker' or 'kruskal'). Defaults to
                "backtracker".
            shape (set[tuple[int, int]] | None, optional): A set of (x, y)
                coordinates representing cells to be excluded from path
                generation. Defaults to None.
            perfect (bool, optional): Whether to generate a perfect maze.
                Defaults to True.
            vizualize (bool, optional): Whether to enable visualization
                during generation. Defaults to True.
        """
        if not isinstance(grid, Grid):
            raise TypeError("Expected Grid for grid, "
                            f"got {type(grid).__name__}")
        if not isinstance(width, int):
            raise TypeError("Expected int for width, "
                            f"got {type(width).__name__}")
        if width <= 0:
            raise ValueError("width must be a positive integer greater than 0")
        if not isinstance(height, int):
            raise TypeError("Expected int for height, "
                            f"got {type(height).__name__}")
        if height <= 0:
            raise ValueError("height must be a positive integer "
                             "greater than 0")
        if viz is not None and not isinstance(viz, ConsoleVisualizer):
            raise TypeError("Expected ConsoleVisualizer or None for viz, "
                            f"got {type(viz).__name__}")
        if seed is not None and not isinstance(seed, (str, int)):
            raise TypeError("Expected str, int, or None for seed, "
                            f"got {type(seed).__name__}")
        if not isinstance(algorithm_name, str):
            raise TypeError("Expected str for algorithm_name, "
                            f"got {type(algorithm_name).__name__}")
        if not algorithm_name.strip():
            raise ValueError("algorithm_name cannot be an empty string")
        if shape is not None:
            if not isinstance(shape, set):
                raise TypeError("Expected set or None for shape, "
                                f"got {type(shape).__name__}")
            for item in shape:
                if (not isinstance(item, tuple) or len(item) != 2 or
                        not isinstance(item[0], int) or
                        not isinstance(item[1], int)):
                    raise TypeError("Expected set of tuples of two integers "
                                    "for shape")
        if not isinstance(perfect, bool):
            raise TypeError("Expected bool for perfect, "
                            f"got {type(perfect).__name__}")
        if not isinstance(vizualize, bool):
            raise TypeError("Expected bool for vizualize, "
                            f"got {type(vizualize).__name__}")

        self.width = width
        self.height = height
        self.grid = grid
        self.shape: set[tuple[int, int]] | None = shape
        self.rng = random.Random()
        if seed is not None:
            self.rng.seed(seed)
        self.algorithm_name = algorithm_name
        self.viz = viz
        self.perfect = perfect
        self.vizualize = vizualize

    def generate(self) -> None:
        """Execute the selected maze generation algorithm.

        Instantiates the appropriate generation strategy based on the
        configured algorithm name and applies it to the grid. If
        visualization is
        enabled, it renders the initial state before applying the strategy.

        Raises:
            ValueError: If the configured algorithm name is not a
                supported strategy.
        """
        if self.viz:
            self.viz.shape = self.shape if self.shape else set()
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
