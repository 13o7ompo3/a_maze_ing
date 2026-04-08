from abc import ABC, abstractmethod
from random import Random
from mazegen.grid import Grid
from mazegen.visualizer import ConsoleVisualizer
from time import sleep


class GenerationStrategy(ABC):
    """Define the base interface for maze generation strategies.

    This abstract base class establishes the common properties and methods
    required for any algorithm that generates mazes within the grid.
    """

    def __init__(self, grid: Grid, rng: Random,
                 viz: ConsoleVisualizer | None = None, perfect: bool = True,
                 vizualize: bool = True):
        """Initialize the base GenerationStrategy.

        Args:
            grid (Grid): The maze grid object to be manipulated.
            rng (Random): The random number generator instance.
            viz (ConsoleVisualizer | None, optional): The visualizer object
                for rendering. Defaults to None.
            perfect (bool, optional): Whether to generate a perfect maze
                (no loops). Defaults to True.
            vizualize (bool, optional): Whether to enable visualization.
                Defaults to True.
        """
        if not isinstance(grid, Grid):
            raise TypeError("Expected Grid for grid, "
                            f"got {type(grid).__name__}")
        if not isinstance(rng, Random):
            raise TypeError("Expected Random for rng, "
                            f"got {type(rng).__name__}")
        if viz is not None and not isinstance(viz, ConsoleVisualizer):
            raise TypeError("Expected ConsoleVisualizer or None for viz, "
                            f"got {type(viz).__name__}")
        if not isinstance(perfect, bool):
            raise TypeError("Expected bool for perfect, "
                            f"got {type(perfect).__name__}")
        if not isinstance(vizualize, bool):
            raise TypeError("Expected bool for vizualize, "
                            f"got {type(vizualize).__name__}")
        self.grid = grid
        self.rng = rng
        self.viz = viz
        self.perfect = perfect
        self.vizualize = vizualize

    @abstractmethod
    def apply(self) -> None:
        """Apply the maze generation algorithm to the grid.

        Subclasses must override this method to implement their specific
        maze generation logic.
        """
        pass

    def imperfect_maze(self, rejected_edges: list[tuple[
            tuple[int, int], tuple[int, int], int, int]]) -> None:
        """Introduce loops into the maze to make it imperfect.

        Randomly removes a percentage of rejected walls (edges) to create
        loops, ensuring that no 2x2 open rooms are formed in the process.

        Args:
            rejected_edges (list): A list of tuples containing the
                rejected walls and cells during the perfect maze
                generation process.
        """
        if not isinstance(rejected_edges, list):
            raise TypeError("Expected list for rejected_edges, "
                            f"got {type(rejected_edges).__name__}")
        if not all(isinstance(edge, tuple) and len(edge) == 4
                   for edge in rejected_edges):
            raise TypeError("Expected list of tuples of length 4 for "
                            "rejected_edges")
        w, h = self.grid.width, self.grid.height
        p_c = 0.05
        k = int(p_c * ((w * h) - w - h + 1))
        self.rng.shuffle(rejected_edges)

        for cell_a, cell_b, wall_a, wall_b in rejected_edges:
            if k <= 0:
                break

            x, y = cell_a
            nx, ny = cell_b

            if not self._creates_2x2_room(x, y, nx, ny, wall_a):

                self.grid.remove_wall(x, y, wall_a)
                self.grid.remove_wall(nx, ny, wall_b)
                k -= 1

                if self.viz and self.vizualize:
                    sleep(0.04)
                    self.viz.render_cells(x, y)
                    self.viz.render_cells(nx, ny)

    def _creates_2x2_room(self, x: int, y: int, nx: int, ny: int,
                          wall: int) -> bool:
        """Check if removing the wall between (x, y) and (nx, ny) creates a
        2x2 room.

        Depending on the wall being removed, it checks the adjacent cells
        to see if they form a 2x2 room (e.g. if removing a vertical wall,
        it checks the cells above and below the two cells).
        Example of a 2x2 room:
        +---+---+
        |   |   |
        +---+---+
        |   |   |
        +---+---+

        Args:
            x (int): The x-coordinate of the first cell.
            y (int): The y-coordinate of the first cell.
            nx (int): The x-coordinate of the second cell.
            ny (int): The y-coordinate of the second cell.
            wall (int): The bitmask value of the wall to remove.

        Returns:
            bool: True if a 2x2 room is created, False otherwise.
        """
        if not isinstance(x, int):
            raise TypeError(f"Expected int for x, got {type(x).__name__}")
        if not isinstance(y, int):
            raise TypeError(f"Expected int for y, got {type(y).__name__}")
        if not isinstance(nx, int):
            raise TypeError(f"Expected int for nx, got {type(nx).__name__}")
        if not isinstance(ny, int):
            raise TypeError(f"Expected int for ny, got {type(ny).__name__}")
        if not isinstance(wall, int):
            raise TypeError("Expected int for wall, "
                            f"got {type(wall).__name__}")
        if x < 0 or y < 0 or nx < 0 or ny < 0:
            raise ValueError("Coordinates cannot be negative")
        if wall not in {1, 2, 4, 8}:
            raise ValueError(f"Invalid wall bitmask: {wall}. "
                             "Expected 1, 2, 4, or 8.")
        gv = self.grid.get_value
        w, h = self.grid.width, self.grid.height

        """
    in the code below i handele two of the four cases (wall = 1 and wall = 8)

        Case handed:
                      +---+
        +---+---+     | 1 |
        | 1 | 2 | and +---+
        +---+---+     | 2 |
                      +---+

        So, by just swapping the values,
        i can handle both cases with the same code.
        """
        if wall == 1:
            x, nx = nx, x
            y, ny = ny, y
            wall = 4
        elif wall == 8:
            x, nx = nx, x
            y, ny = ny, y
            wall = 2

        if wall == 2:
            if y > 0 and not ((gv(x, y) & 1) or (gv(nx, ny) & 1) or
                              (gv(x, y - 1) & 2)):
                return True
            if y < h - 1 and not ((gv(x, y) & 4) or (gv(nx, ny) & 4) or
                                  (gv(x, y + 1) & 2)):
                return True
        elif wall == 4:
            if x > 0 and not ((gv(x, y) & 8) or (gv(nx, ny) & 8) or
                              (gv(x - 1, y) & 4)):
                return True
            if x < w - 1 and not ((gv(x, y) & 2) or (gv(nx, ny) & 2) or
                                  (gv(x + 1, y) & 4)):
                return True

        return False


class SolverStrategy(ABC):
    """Define the base interface for maze solving strategies.

    This abstract base class establishes the common properties and methods
    required for any algorithm that solves mazes.
    """

    def __init__(self, grid: Grid, entry: tuple[int, int],
                 exit: tuple[int, int],
                 viz: ConsoleVisualizer | None = None,
                 vizualize: bool = True) -> None:
        """Initialize the base SolverStrategy.

        Args:
            grid (Grid): The maze grid object to be solved.
            entry (tuple[int, int]): The (x, y) coordinates of the
                maze entry point.
            exit (tuple[int, int]): The (x, y) coordinates of the
                maze exit point.
            viz (ConsoleVisualizer | None, optional): The visualizer object
                for rendering. Defaults to None.
            vizualize (bool, optional): Whether to enable visualization.
                Defaults to True.
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
        self.vizualize = vizualize

    @abstractmethod
    def solve(self) -> str:
        """Execute the maze solving algorithm.

        Subclasses must override this method to implement their specific
        maze solving logic.

        Returns:
            str: A string of directional characters ('N', 'S', 'E', 'W')
                representing the solution path.
        """
        pass
