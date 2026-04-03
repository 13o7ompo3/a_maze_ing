from abc import ABC, abstractmethod
from random import Random
from mazegen.grid import Grid
from mazegen.visualizer import ConsoleVisualizer
from time import sleep


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

    def imperfect_maze(self, rejected_edges: list) -> None:
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
        """
    Check if removing the wall between (x, y) and (nx, ny) creates a 2x2 room.

        example of a 2x2 room:
        +---+---+
        |   |   |
        +---+---+
        |   |   |
        +---+---+

        Args:
            x (int): x coordinate of the first cell
            y (int): y coordinate of the first cell
            nx (int): x coordinate of the second cell
            ny (int): y coordinate of the second cell
            wall (int): wall to remove

        Returns:
            bool: True if the 2x2 room is created, False otherwise

        How it works:
        - Depending on the wall being removed, we check the adjacent cells to see if they form a 2x2 room.
        - For example, if we're removing a vertical wall (wall == 2), we check the cells above and below the two cells. If both pairs of cells have no wall between them, then we have a 2x2 room.
        """
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
