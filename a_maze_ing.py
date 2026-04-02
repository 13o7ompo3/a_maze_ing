import sys
import os
from mazegen.grid import Grid
from mazegen.generator import MazeGenerator
from mazegen.utils import save_maze
from mazegen.visualizer import ConsoleVisualizer
from mazegen.solver import MazeSolver
import time
import tty
import termios

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


def parse_config(filepath: str) -> dict:
    config = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if not (key and value):
                    raise ValueError("Bad format")
                if key in config:
                    raise ValueError("Duplicated key")
                config[key.strip()] = value.strip()
            except Exception as e:
                raise ValueError(f"{e}: {line}")
    return config


def check_output_file(filepath: str) -> None:
    pass  # to be implemented


def check_for_expectedvalue(config: dict, key: str,
                            expected_values: set) -> None:
    if key in config and config[key].lower() not in expected_values:
        raise ValueError(f"Invalid value for {key}. "
                         f"Expected one of: {expected_values}")


def parse(filepath: str) -> dict:
    config = {}
    required_keys = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                     "PERFECT"}
    bonus_keys = {"SEED", "ALGORITHM", "STRATEGY", "VIZUALIZE"}

    config = parse_config(filepath)

    if not required_keys.issubset(config.keys()):
        missing = required_keys - config.keys()
        raise ValueError(f"Missing mandatory keys: {missing}")
    if not set(config.keys()).issubset(required_keys | bonus_keys):
        extra = set(config.keys()) - (required_keys | bonus_keys)
        raise ValueError(f"Invalid keys: {extra}")

    try:
        config['WIDTH'] = int(config['WIDTH'])
        config['HEIGHT'] = int(config['HEIGHT'])
    except ValueError:
        raise ValueError("Invalid WIDTH or HEIGHT is not a number")
    try:
        config['ENTRY'] = tuple(map(int, config['ENTRY'].split(',', 1)))
        config['EXIT'] = tuple(map(int, config['EXIT'].split(',', 1)))
    except ValueError:
        raise ValueError("Invalid ENTRY or EXIT, example: ENTRY=20,20")

    # verify output file is valid
    check_output_file(config['OUTPUT_FILE'])

    config['ALGORITHM'] = config.get('ALGORITHM', 'backtracker').lower()
    config['STRATEGY'] = config.get('STRATEGY', 'bfs').lower()
    config['VIZUALIZE'] = config.get('VIZUALIZE', 'true').lower() == 'true'
    config['PERFECT'] = config.get('PERFECT', 'true').lower() == 'true'
    check_for_expectedvalue(config, 'ALGORITHM', {'backtracker', 'kruskal'})
    check_for_expectedvalue(config, 'STRATEGY', {'bfs', 'dfs'})
    check_for_expectedvalue(config, 'VIZUALIZE', {'true', 'false'})
    check_for_expectedvalue(config, 'PERFECT', {'true', 'false'})

    return config


def get_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def parce_input() -> tuple[tuple[int, int], int, int, int]:
    ch = get_key()

    c = None
    wall = None
    opp_wall = None
    return_code = None

    if ch == '\x1b[A':
        c = (0, -1)
        wall = 1
        opp_wall = 4
    elif ch == '\x1b[B':
        c = (0, 1)
        wall = 4
        opp_wall = 1
    elif ch == '\x1b[D':
        c = (-1, 0)
        wall = 8
        opp_wall = 2
    elif ch == '\x1b[C':
        c = (1, 0)
        wall = 2
        opp_wall = 8
    elif ch == '1':
        return_code = 1
    elif ch == '2':
        return_code = 2
    elif ch == 'q':
        return_code = 3
    if c is not None:
        return_code = 0

    return c, wall, opp_wall, return_code


def player_mode(grid: Grid, viz: ConsoleVisualizer) -> None:
    break_mode = False
    exit = False
    viz.player = (0, 0)
    viz.render()
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    # Move cursor below the maze to print menu
    while True:
        sys.stdout.write(f"\033[{2 * grid.height + 3};1H")
        print("=== Player Mod ===")
        print(f"1. {'Hide' if viz.show_path else 'Show'} path")
        print(f"2. breake mode: {break_mode} ")
        print("Press 'q' to quit player mode")
        while True:
            x, y = viz.player
            c, wall, opp_wall, input_code = parce_input()
            if input_code == 0:
                cx, cy = c
                cx += x
                cy += y
                if not (cx < 0 or cy < 0 or
                        cx >= grid.width or cy >= grid.height
                        or (cx, cy) in viz.imprint_42):
                    if break_mode:
                        grid.remove_wall(x, y, wall)
                        grid.remove_wall(cx, cy, opp_wall)
                    if not (grid.get_value(x, y) & wall):
                        viz.player = (cx, cy)
                    viz.render_cells(x, y)
                    viz.render_cells(cx, cy)
            elif input_code == 1:
                viz.show_path = not viz.show_path
                viz.render()
                break
            elif input_code == 2:
                break_mode = not break_mode
                break
            elif input_code == 3:
                exit = True
                break
        if exit:
            break
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
    viz.player = None


if __name__ == "__main__":
    try:
        exit = False
        config = parse_config(sys.argv[1])
        color_idx = 0
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        while True:
            if 'SEED' not in config:
                seed = int(time.time() * 1000)
            else:
                seed = config['SEED']
            grid = Grid(config['WIDTH'], config['HEIGHT'])
            viz = ConsoleVisualizer(grid, config['ENTRY'],
                                    config['EXIT'])
            viz.imprint_42 = set()
            viz.color_idx = color_idx
            generator = MazeGenerator(grid, config['WIDTH'], config['HEIGHT'],
                                      viz, seed, config['ALGORITHM'],
                                      config['PERFECT'], config['VIZUALIZE'])
            generator.generate()
            solver = MazeSolver(grid, viz)
            solution_path = solver.solve(config['ENTRY'], config['EXIT'],
                                         config['STRATEGY'])

            save_maze(grid, config['ENTRY'], config['EXIT'],
                      solution_path, config['OUTPUT_FILE'])

            viz.set_path(solution_path)

            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                viz.render()
                print("\n=== A-Maze-ing Menu ===")
                print("1. Re-generate new maze")
                print(f"2. {'Hide' if viz.show_path else 'Show'} path")
                print("3. Change colors")
                print(f"4. change algorithm : {config['ALGORITHM']}")
                print(f"5. change strategy : {config['STRATEGY']}")
                print("6. Solve maze")
                print("7. Player mode")
                print("q. Quit")

                choice = get_key()
                os.system('cls' if os.name == 'nt' else 'clear')

                if choice == '1':
                    break
                elif choice == '2':
                    viz.show_path = not viz.show_path
                elif choice == '3':
                    color_idx = (color_idx + 1) % len(COLORS)
                    viz.color_idx = color_idx
                elif choice == '4':
                    if config['ALGORITHM'] == 'backtracker':
                        new_algorithm = 'kruskal'
                    elif config['ALGORITHM'] == 'kruskal':
                        new_algorithm = 'backtracker'
                    config['ALGORITHM'] = new_algorithm
                elif choice == '5':
                    if config['STRATEGY'] == 'bfs':
                        new_strategy = 'dfs'
                    elif config['STRATEGY'] == 'dfs':
                        new_strategy = 'bfs'

                    config['STRATEGY'] = new_strategy
                elif choice == '6':
                    solution_path = solver.solve(config['ENTRY'],
                                                 config['EXIT'],
                                                 config['STRATEGY'])
                    viz.set_path(solution_path)
                elif choice == '7':
                    player_mode(grid, viz)
                elif choice == 'q':
                    exit = True
                    break
            if exit:
                break
    except BaseException as e:
        sys.stdout.write("\033[?25h")
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.flush()
        print(f"Error: {e}")
        sys.exit(1)

    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Goodbye!")
