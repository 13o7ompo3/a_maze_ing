import sys
import os
from mazegen.grid import Grid
from mazegen.generator import MazeGenerator
from mazegen.utils import save_maze
from mazegen.visualizer import ConsoleVisualizer
from mazegen.solver import MazeSolver
import time

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
    required_keys = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                     "PERFECT"}
    bonus_keys = {"SEED", "ALGORITHM", "STRATEGY"}

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                key, value = line.split('=', 1)
                if not key.strip() and not value.strip():
                    continue
                config[key.strip()] = value.strip()
                if not config[key.strip()]:
                    raise ValueError()
            except ValueError:
                raise ValueError(f"Bad format: {line}")

    if not required_keys.issubset(config.keys()):
        missing = required_keys - config.keys()
        raise ValueError(f"Missing mandatory keys: {missing}")
    if not set(config.keys()).issubset(required_keys | bonus_keys):
        extra = set(config.keys()) - (required_keys | bonus_keys)
        raise ValueError(f"Invalid keys: {extra}")

    try:
        config['WIDTH'] = int(config['WIDTH'])
        config['HEIGHT'] = int(config['HEIGHT'])
        config['ENTRY'] = tuple(map(int, config['ENTRY'].split(',')))
        config['EXIT'] = tuple(map(int, config['EXIT'].split(',')))
    except (ValueError, IndexError):
        raise ValueError("Invalid number format in config")
    # if 'SEED' not in config:
    #     config['SEED'] = int(time.time() * 1000)
    if 'ALGORITHM' not in config:
        config['ALGORITHM'] = "backtracker"
    if 'STRATEGY' not in config:
        config['STRATEGY'] = "bfs"
    return config


if __name__ == "__main__":
    try:

        config = parse_config(sys.argv[1])
        color_idx = 0

        while True:
            if 'SEED' not in config:
                seed = int(time.time() * 1000)
            else:
                seed = int(config['SEED'])
            grid = Grid(config['WIDTH'], config['HEIGHT'])
            viz = ConsoleVisualizer(grid, config['ENTRY'],
                                    config['EXIT'])
            viz.imprint_42 = set()
            viz.color_idx = color_idx
            generator = MazeGenerator(grid, config['WIDTH'], config['HEIGHT'],
                                      viz, seed, config['ALGORITHM'])
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
                print("q. Quit")

                choice = input("Choice? (1-5 or q to quit): ").strip()
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
                    solution_path = solver.solve(config['ENTRY'], config['EXIT'],
                                         config['STRATEGY'])
                    viz.set_path(solution_path)
                elif choice == 'q':
                    print("Goodbye!")
                    sys.exit(0)
                else:
                    print("Invalid choice.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
