import os
import sys
import shutil
import time
import tty
import termios

from mazegen.grid import Grid
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver
from mazegen.utils import save_maze
from mazegen.utils import cell_42
from mazegen.visualizer import ConsoleVisualizer
from typing import Any


# Display constants


COLORS = [
    "\033[97m",  # White
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[94m",  # Blue
    "\033[93m",  # Yellow
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
]
RESET = "\033[0m"

AMAZEING_ART = [
    "   █████████              ██████   ██████   █████████   ███████████"
    " ██████████            █████ ██████   █████   █████████ ",
    "  ███░░░░░███            ░░██████ ██████   ███░░░░░███ ░█░░░░░░███ "
    "░░███░░░░░█           ░░███ ░░██████ ░░███   ███░░░░░███",
    " ░███    ░███             ░███░█████░███  ░███    ░███ ░     ███░  "
    " ░███  █ ░             ░███  ░███░███ ░███  ███     ░░░ ",
    " ░███████████  ██████████ ░███░░███ ░███  ░███████████      ███    "
    " ░██████    ██████████ ░███  ░███░░███░███ ░███         ",
    " ░███░░░░░███ ░░░░░░░░░░  ░███ ░░░  ░███  ░███░░░░░███     ███     "
    " ░███░░█   ░░░░░░░░░░  ░███  ░███ ░░██████ ░███    █████",
    " ░███    ░███             ░███      ░███  ░███    ░███   ████     █"
    " ░███ ░   █            ░███  ░███  ░░█████ ░░███  ░░███ ",
    " █████   █████            █████     █████ █████   █████ ███████████"
    " ██████████            █████ █████  ░░█████ ░░█████████ ",
    "░░░░░   ░░░░░            ░░░░░     ░░░░░ ░░░░░   ░░░░░ ░░░░░░░░░░░ "
    "░░░░░░░░░░            ░░░░░ ░░░░░    ░░░░░   ░░░░░░░░░  ",
]

YOU_WIN_ART = [
    " █████ █████                        █████   ███   █████  ███             "
    "   ███",
    "░░███ ░░███                        ░░███   ░███  ░░███  ░░░              "
    "  ░███",
    " ░░███ ███    ██████  █████ ████    ░███   ░███   ░███  ████  ████████   "
    "  ░███",
    "  ░░█████    ███░░███░░███ ░███     ░███   ░███   ░███ ░░███ ░░███░░███  "
    "  ░███",
    "   ░░███    ░███ ░███ ░███ ░███     ░░███  █████  ███   ░███  ░███ ░███  "
    "  ░███",
    "    ░███    ░███ ░███ ░███ ░███      ░░░█████░█████░    ░███  ░███ ░███  "
    "  ░░░ ",
    "    █████   ░░██████  ░░████████       ░░███ ░░███      █████ ████ █████ "
    "   ███",
    "   ░░░░░     ░░░░░░    ░░░░░░░░         ░░░   ░░░      ░░░░░ ░░░░ ░░░░░  "
    "  ░░░ ",
]


# Config parsing

def _parse_raw_config(filepath: str) -> dict[str, str]:
    """Parse a configuration file into a dictionary.

    Reads a file line by line, ignoring empty lines and comments
    (starting with '#'). Splits each valid line by '=' to extract
    key-value pairs.

    Args:
        filepath (str): The path to the configuration file.

    Returns:
        dict: A dictionary containing the parsed configuration keys and values.

    Raises:
        ValueError: If a line has a bad format or if a duplicated key is found.
    """
    if not os.path.isfile(filepath):
        raise ValueError(f"Config file not found: {filepath}")

    config = {}
    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not (key and value):
                    raise ValueError("Bad format")
                if key in config:
                    raise ValueError(f"Duplicate key '{key}'")
                config[key] = value
            except Exception as e:
                raise ValueError(f"Line {line_num}: {e}")

    return config


def _check_output_file(filepath: str) -> None:
    """Check if the given output file path is valid.

    Verifies that the directory of the file path exists and that the file path
    is not empty.

    Args:
        filepath (str): The path to the output file to check.

    Raises:
        ValueError: If the directory does not exist or the filepath is empty.
    """
    if not filepath.strip():
        raise ValueError("OUTPUT_FILE cannot be empty")
    directory = os.path.dirname(filepath)
    if directory and not os.path.isdir(directory):
        raise ValueError(f"Output directory does not exist: {directory}")
    if not os.path.exists(filepath):
        return
    if not os.path.isfile(filepath):
        raise IsADirectoryError(f"Output file does not exist: {filepath}")
    if not os.access(filepath, os.W_OK):
        raise PermissionError(f"Output file is not writable: {filepath}")


def _check_expected_value(config: dict[str, Any], key: str,
                          expected_values: set[str]) -> None:
    """Check if a specific configuration key has an expected value.

    Args:
        config (dict[str, Any]): The configuration dictionary.
        key (str): The configuration key to check.
        expected_values (set): A set of valid values for the given key.

    Raises:
        ValueError: If the key exists in the config but its value is not
            in expected_values.
    """
    if key in config and config[key] not in expected_values:
        raise ValueError(
            f"Invalid value for {key}. Expected one of: {expected_values}"
        )


def parse(filepath: str) -> dict[str, Any]:
    """Parse and validate the configuration file for the maze generator.

    Loads the configuration using `parse_config` and validates all required
    and optional keys. It ensures that dimensions and coordinates are valid
    integers, and applies default values where optional keys are missing.

    Args:
        filepath (str): The path to the configuration file.

    Returns:
     dict[str, Any]: A fully validated and populated configuration dictionary.

    Raises:
        ValueError: If mandatory keys are missing, invalid keys are present,
            or any value fails validation (e.g., non-integers for dimensions,
            out of bounds coordinates, entry/exit conflicts).
    """
    required_keys = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                     "PERFECT"}
    bonus_keys = {"SEED", "ALGORITHM", "STRATEGY", "VIZUALIZE"}

    config: dict[str, Any] = dict(_parse_raw_config(filepath))

    missing = required_keys - config.keys()
    if missing:
        raise ValueError(f"Missing mandatory keys: {missing}")

    extra = config.keys() - (required_keys | bonus_keys)
    if extra:
        raise ValueError(f"Invalid keys: {extra}")

    # Numeric dimensions
    try:
        config["WIDTH"] = int(config["WIDTH"])
        config["HEIGHT"] = int(config["HEIGHT"])
    except ValueError:
        raise ValueError("Invalid WIDTH or HEIGHT is not a number")
    if config["WIDTH"] < 1 or config["HEIGHT"] < 1:
        raise ValueError("WIDTH and HEIGHT must be positive integers")

    # Entry / exit coordinates
    try:
        config["ENTRY"] = tuple(map(int, config["ENTRY"].split(",", 1)))
        config["EXIT"] = tuple(map(int, config["EXIT"].split(",", 1)))
    except ValueError:
        raise ValueError("Invalid ENTRY or EXIT, example: ENTRY=20,20")

    _check_output_file(config["OUTPUT_FILE"])

    w, h = config["WIDTH"], config["HEIGHT"]
    for key in ("ENTRY", "EXIT"):
        x, y = config[key]
        if not (0 <= x < w and 0 <= y < h):
            raise ValueError(
                f"{key}={config[key]} is outside maze bounds ({w}x{h})"
            )

    if config["ENTRY"] == config["EXIT"]:
        raise ValueError("ENTRY and EXIT must be different cells")

    config["SEED"] = config.get("SEED", None)
    # Normalize boolean-like string values before validation
    for key in ("PERFECT", "VIZUALIZE"):
        if key in config:
            config[key] = config[key].lower()

    _check_expected_value(config, "PERFECT", {"true", "false"})
    _check_expected_value(config, "VIZUALIZE", {"true", "false"})

    # Resolve optional keys with defaults
    config["ALGORITHM"] = config.get("ALGORITHM", "backtracker").lower()
    config["STRATEGY"] = config.get("STRATEGY", "bfs").lower()
    config["VIZUALIZE"] = config.get("VIZUALIZE", "true") == "true"
    config["PERFECT"] = config.get("PERFECT", "true") == "true"

    _check_expected_value(config, "ALGORITHM", {"backtracker", "kruskal"})
    _check_expected_value(config, "STRATEGY", {"bfs", "dfs"})

    return config


# Terminal / input helpers
def _get_key() -> str:
    """Read a single keypress from the standard input.

    Uses `tty` and `termios` to read a character without waiting for the Enter
    key. It also handles escape sequences for arrow keys.

    Returns:
        str: The character or escape sequence read from standard input.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def _parse_input() -> tuple[Any, Any, Any, Any]:
    """Translate a raw keypress into movement/action components.

    Returns:
    tuple: A tuple containing:
        (direction, wall, opposite_wall, return_code)
        - direction is (dx, dy) or None for non-movement keys.
        - wall / opposite_wall are bitmask values used by the grid.
        - return_code: 0 = moved, 1 = toggle path, 2 = break mode,
                       3 = quit, None = unrecognised key.
    """
    ch = _get_key()

    direction = None
    wall = None
    opp_wall = None
    return_code = None

    key_map = {
        "\x1b[A": ((0, -1), 1, 4),   # Up
        "\x1b[B": ((0,  1), 4, 1),   # Down
        "\x1b[D": ((-1, 0), 8, 2),   # Left
        "\x1b[C": ((1,  0), 2, 8),   # Right
    }

    if ch in key_map:
        direction, wall, opp_wall = key_map[ch]
        return_code = 0
    elif ch == "1":
        return_code = 1
    elif ch == "2":
        return_code = 2
    elif ch == "q":
        return_code = 3

    return direction, wall, opp_wall, return_code


def check_terminal_size(grid: Grid) -> None:
    """ Check if the terminal is large enough to display the maze and menu.

    Args:
        grid (Grid): The maze grid object.
    """
    term_w, term_h = shutil.get_terminal_size((120, 30))
    maze_width = grid.width * 4 + 1
    maze_height = grid.height * 2 + 1
    required_height = maze_height + 8

    if maze_width > term_w:
        raise ValueError(
            f"Terminal too small (width={term_w}). "
            f"Need at least {maze_width} columns."
        )
    if required_height > term_h:
        raise ValueError(
            f"Terminal too small (height={term_h}). "
            f"Need at least {required_height} rows."
        )


# UI rendering helpers

def print_art(art: list[str]) -> None:
    """Print ASCII art centered in the terminal.

    Clears the terminal, calculates the center position based on the terminal
    size, and prints each line of the provided ASCII art. Pauses for 5 seconds
    before clearing the screen again.

    Args:
        art (list[str]): A list of strings representing the ASCII art lines.
    """
    os.system("cls" if os.name == "nt" else "clear")
    term_w, term_h = shutil.get_terminal_size((120, 30))
    start_y = max(1, term_h // 2 - len(art) // 2)
    for i, line in enumerate(art):
        start_x = max(1, term_w // 2 - len(line) // 2)
        sys.stdout.write(f"\033[{start_y + i};{start_x}H{line}")
    sys.stdout.flush()
    time.sleep(3)
    os.system("cls" if os.name == "nt" else "clear")


def _render_main_menu(grid: Grid, viz: ConsoleVisualizer,
                      config: dict[str, Any]) -> None:
    """Overwrite the menu area below the maze with the current menu state.

    Arguments:
        grid (Grid): The maze grid object.
        viz (ConsoleVisualizer): The visualizer object for rendering the maze.
        config (dict): The configuration dictionary.
    """
    start_row = 2 * grid.height + 3
    lines = [
        "=== A-Maze-ing Menu ===",
        "1. Re-generate new maze",
        f"2. {'Hide' if viz.show_path else 'Show'} path",
        "3. Change colors",
        f"4. change algorithm : {config['ALGORITHM']}",
        f"5. change strategy : {config['STRATEGY']}",
        "6. Solve maze",
        "7. Player mode",
        f"8. Animation : {config['VIZUALIZE']} ",
        "Q. Quit",
    ]
    for i, line in enumerate(lines):
        sys.stdout.write(f"\033[{start_row + i};1H\033[2K{line}")
    sys.stdout.flush()


# Game modes

def _player_mode(grid: Grid, viz: ConsoleVisualizer) -> None:
    """Execute the interactive player mode for solving the maze.

    Allows the user to manually navigate through the maze using arrow keys,
    toggle the path visibility, and enable 'break mode' to break through walls.
    The mode ends when the user reaches the exit or chooses to quit.

    Args:
        grid (Grid): The maze grid object.
        viz (ConsoleVisualizer): The visualizer object for rendering the maze.
    """
    break_mode = False
    viz.player = viz.entry
    os.system("cls" if os.name == "nt" else "clear")
    check_terminal_size(grid)
    viz.render()

    exiting = False
    while not exiting:
        # Render the player-mode sub-menu below the maze
        sys.stdout.write(f"\033[{2 * grid.height + 3};1H\033[J")
        print("=== Player Mod ===")
        print(f"1. {'Hide' if viz.show_path else 'Show'} path")
        print(f"2. break mode: {break_mode} ")
        print("Press 'q' to quit player mode")

        while True:
            x, y = viz.player
            direction, wall, opp_wall, input_code = _parse_input()

            if input_code == 0:
                dx, dy = direction
                nx, ny = x + dx, y + dy
                in_bounds = 0 <= nx < grid.width and 0 <= ny < grid.height
                not_imprint = (nx, ny) not in viz.shape

                if in_bounds and not_imprint:
                    if break_mode:
                        grid.remove_wall(x, y, wall)
                        grid.remove_wall(nx, ny, opp_wall)
                    if not (grid.get_value(x, y) & wall):
                        viz.player = (nx, ny)
                    viz.render_cells(x, y)
                    viz.render_cells(nx, ny)

                if viz.player == viz.exit:
                    print_art(YOU_WIN_ART)
                    exiting = True
                    break

            elif input_code == 1:
                viz.show_path = not viz.show_path
                check_terminal_size(grid)
                viz.render()
                break  # Redraw sub-menu

            elif input_code == 2:
                break_mode = not break_mode
                break  # Redraw sub-menu

            elif input_code == 3:
                exiting = True
                break

    viz.player = None


# Main loop

def main() -> None:
    """Entry point: parse config,
    run the main maze generation / interaction loop."""
    if len(sys.argv) == 2:
        config_file = sys.argv[1]
    else:
        raise ValueError("Usage: python a_maze_ing.py <config_file>")
    config = parse(config_file)

    color_idx = 0

    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[?25l")  # Hide cursor
    sys.stdout.flush()
    print_art(AMAZEING_ART)

    grid = Grid(config["WIDTH"], config["HEIGHT"])
    viz = ConsoleVisualizer(grid, config["ENTRY"], config["EXIT"])
    generator = MazeGenerator(
        grid, config["WIDTH"], config["HEIGHT"],
        viz, config["SEED"], config["ALGORITHM"],
        cell_42(config["WIDTH"], config["HEIGHT"]),
        config["PERFECT"], config["VIZUALIZE"],
    )
    if not generator.shape:
        raise ValueError("Maze too small to generate 42 pattern")
    if config["ENTRY"] in generator.shape or config["EXIT"] in generator.shape:
        raise ValueError("ENTRY or EXIT is inside the 42 pattern")
    solver = MazeSolver(
        grid, config["ENTRY"], config["EXIT"],
        viz, config["STRATEGY"], config["VIZUALIZE"],
    )
    viz.color_idx = color_idx

    exiting = False
    while not exiting:
        # --- Generate a new maze ---
        viz.show_path = False
        generator.rng.seed(config['SEED'])
        grid.cells = [15] * (grid.width * grid.height)
        viz.set_path("")
        viz.render()
        generator.generate()
        solution_path = solver.solve()
        viz.set_path(solution_path)
        save_maze(grid, config['ENTRY'], config['EXIT'],
                  solution_path, config['OUTPUT_FILE'])
        check_terminal_size(grid)
        viz.render()

        # --- Main menu loop ---
        menu_dirty = True
        while True:
            if menu_dirty:
                _render_main_menu(grid, viz, config)
                menu_dirty = False

            choice = _get_key()

            if choice == "1":
                break  # Regenerate maze

            elif choice == "2":
                viz.show_path = not viz.show_path
                check_terminal_size(grid)
                viz.render()
                menu_dirty = True

            elif choice == "3":
                color_idx = (color_idx + 1) % len(COLORS)
                viz.color_idx = color_idx
                check_terminal_size(grid)
                viz.render()
                menu_dirty = True

            elif choice == "4":
                config["ALGORITHM"] = (
                    "kruskal" if config["ALGORITHM"] == "backtracker"
                    else "backtracker"
                )
                generator.algorithm_name = config["ALGORITHM"]
                menu_dirty = True

            elif choice == "5":
                config["STRATEGY"] = (
                    "dfs" if config["STRATEGY"] == "bfs" else "bfs"
                )
                solver.strategy = config["STRATEGY"]
                menu_dirty = True

            elif choice == "6":
                viz.render()
                solution_path = solver.solve()
                viz.set_path(solution_path)
                save_maze(
                    grid, config["ENTRY"], config["EXIT"],
                    solution_path, config["OUTPUT_FILE"],
                )
                check_terminal_size(grid)
                viz.render()
                menu_dirty = True

            elif choice == "7":
                _player_mode(grid, viz)
                check_terminal_size(grid)
                viz.render()
                menu_dirty = True
            elif choice == '8':
                config['VIZUALIZE'] = not config['VIZUALIZE']
                generator.vizualize = config['VIZUALIZE']
                solver.vizualize = config['VIZUALIZE']
                menu_dirty = True
            elif choice == "q":
                exiting = True
                break


# Entry point guard

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        print("\nExited by user.")
        sys.exit(0)
    except BaseException as e:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Error: {e}")
        sys.exit(1)

    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
    os.system("cls" if os.name == "nt" else "clear")
    print("Goodbye!")
