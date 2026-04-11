import os
import sys
from mazegen.grid import Grid


COLORS = [
    "\033[97m",  # White
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[94m",  # Blue
    "\033[93m",  # Yellow
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
    "\033[97m"
]
RESET = "\033[0m"


class ConsoleVisualizer:
    """Render the maze and its state to the console using ASCII characters.

    This class manages the visual representation of the maze, updating
    the display with ANSI escape sequences to draw walls, the player,
    paths, and special shapes.
    """

    def __init__(self, grid: Grid, entry: tuple[int, int],
                 exit: tuple[int, int]):
        """Initialize the ConsoleVisualizer with grid and endpoints.

        Args:
            grid (Grid): The maze grid object to be visualized.
            entry (tuple[int, int]): The (x, y) coordinate pair for the entry.
            exit (tuple[int, int]): The (x, y) coordinate pair for the exit.
        """
        if not isinstance(grid, Grid):
            raise TypeError("Expected Grid for grid, "
                            f"got {type(grid).__name__}")
        if not isinstance(entry, tuple):
            raise TypeError("Expected tuple for entry, "
                            f"got {type(entry).__name__}")
        if (len(entry) != 2 or not isinstance(entry[0], int) or
                not isinstance(entry[1], int)):
            raise ValueError("entry must be a tuple of two integers")
        if entry[0] < 0 or entry[1] < 0:
            raise ValueError("entry coordinates cannot be negative")
        if not isinstance(exit, tuple):
            raise TypeError("Expected tuple for exit, "
                            f"got {type(exit).__name__}")
        if (len(exit) != 2 or not isinstance(exit[0], int) or
                not isinstance(exit[1], int)):
            raise ValueError("exit must be a tuple of two integers")
        if exit[0] < 0 or exit[1] < 0:
            raise ValueError("exit coordinates cannot be negative")
        self.grid: Grid = grid
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.player: tuple[int, int] | None = None
        self.path_coords: set[tuple[int, int]] = set()
        self.show_path: bool = True
        self.color_idx: int = 0
        self.shape: set[tuple[int, int]] = set()

    def set_path(self, path_str: str) -> None:
        """Convert a directional movement string into path coordinates.

        Parses a sequence of directions ('N', 'S', 'E', 'W') starting from the
        entry point and updates the `path_coords` set with every visited (x, y)
        coordinate for rendering the solution or player path.

        Args:
            path_str (str): A string of directions representing the path.
        """
        if not isinstance(path_str, str):
            raise TypeError("Expected str for path_str, "
                            f"got {type(path_str).__name__}")
        if not all(c in 'NSEW' for c in path_str):
            raise ValueError("path_str must only contain characters "
                             "'N', 'S', 'E', 'W'")
        x, y = self.entry
        self.path_coords = {(x, y)}
        for move in path_str:
            if move == 'N':
                y -= 1
            elif move == 'S':
                y += 1
            elif move == 'E':
                x += 1
            elif move == 'W':
                x -= 1
            self.path_coords.add((x, y))

    def render(self) -> None:
        """Draw the entire maze grid to the console screen.

        Clears the terminal screen, prints the top-level maze header, and
        iterates through the entire grid to render each individual cell.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"MAZE VISUALIZATION ({self.grid.width}x{self.grid.height})")
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.render_cells(x, y)

    def render_cells(self, x: int, y: int) -> None:
        """Render a specific cell and its walls at the correct console
        position.

        Calculates the terminal position for the given grid coordinates,
        then uses ANSI escape codes to draw the top, middle, and bottom
        segments of the cell. It accounts for wall bits, path visibility,
        player position, and colors.

        Args:
            x (int): The x-coordinate of the cell in the maze grid.
            y (int): The y-coordinate of the cell in the maze grid.
        """
        if not isinstance(x, int):
            raise TypeError(f"Expected int for x, got {type(x).__name__}")
        if not isinstance(y, int):
            raise TypeError(f"Expected int for y, got {type(y).__name__}")
        if x < 0 or x >= self.grid.width:
            raise ValueError(f"x coordinate {x} is out of bounds "
                             f"for width {self.grid.width}")
        if y < 0 or y >= self.grid.height:
            raise ValueError(f"y coordinate {y} is out of bounds "
                             f"for height {self.grid.height}")
        val = self.grid.get_value(x, y)
        wall_color = COLORS[self.color_idx]
        t_x = 4 * x + 1
        t_y = 2 * y + 2
        sys.stdout.write(f"\033[{t_y};{t_x}H")
        top_line = ""
        top_line += f"{wall_color}+{RESET}"
        if val & 1:
            top_line += f"{wall_color}---{RESET}"
        elif (self.show_path and (x, y) in self.path_coords and
              (x, y - 1) in self.path_coords):
            top_line += f"{COLORS[len(COLORS) - 2 - self.color_idx]}"
            top_line += f"███{RESET}"
        else:
            top_line += "   "
        sys.stdout.write(top_line + f"{wall_color}+{RESET}")
        sys.stdout.write(f"\033[{t_y + 1};{t_x}H")
        mid_line = ""
        if val & 8:
            mid_line += f"{wall_color}|{RESET}"
        elif (self.show_path and (x, y) in self.path_coords and
              (x - 1, y) in self.path_coords):
            mid_line += f"{COLORS[len(COLORS) - 2 - self.color_idx]}"
            mid_line += f"█{RESET}"
        else:
            mid_line += " "

        if self.player and (x, y) == self.player:
            mid_line += f"{COLORS[len(COLORS) - 1 - self.color_idx]}"
            mid_line += f" P {RESET}"
        elif (x, y) == self.entry:
            mid_line += " E "
        elif (x, y) == self.exit:
            mid_line += " X "
        elif self.show_path and (x, y) in self.path_coords:
            mid_line += f"{COLORS[len(COLORS) - 2 - self.color_idx]}"
            mid_line += f"███{RESET}"
        elif (x, y) in self.shape:
            mid_line += f"{COLORS[len(COLORS) - 1 - self.color_idx]}"
            mid_line += f"███{RESET}"
        else:
            mid_line += "   "
        if x == self.grid.width - 1:
            if val & 2:
                mid_line += f"{wall_color}|{RESET}"
            else:
                mid_line += " "
        sys.stdout.write(mid_line)
        sys.stdout.write(f"\033[{t_y + 2};{t_x}H")
        if y == self.grid.height - 1:
            bot_line = ""
            bot_line += f"{wall_color}+{RESET}"
            if val & 4:
                bot_line += f"{wall_color}---{RESET}"
            else:
                bot_line += "   "
            sys.stdout.write(bot_line + f"{wall_color}+{RESET}")
        sys.stdout.flush()
