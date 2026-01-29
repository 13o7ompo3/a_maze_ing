import sys
from mazegen.grid import Grid
from mazegen.generator import MazeGenerator
from mazegen.utils import save_maze
from mazegen.visualizer import ConsoleVisualizer
import time

COLORS = [
    "\033[97m",  # White
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[94m",  # Blue
    "\033[93m",  # Yellow
]
RESET = "\033[0m"


def parse_config(filepath: str) -> dict:
    config = {}
    required_keys = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                     "PERFECT"}

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
            except ValueError:
                raise ValueError(f"Bad format: {line}")

    if not required_keys.issubset(config.keys()):
        missing = required_keys - config.keys()
        raise ValueError(f"Missing mandatory keys: {missing}")

    try:
        config['WIDTH'] = int(config['WIDTH'])
        config['HEIGHT'] = int(config['HEIGHT'])
        config['ENTRY'] = tuple(map(int, config['ENTRY'].split(',')))
        config['EXIT'] = tuple(map(int, config['EXIT'].split(',')))
    except (ValueError, IndexError):
        raise ValueError("Invalid number format in config")
    if 'SEED' in config:
        try:
            config['SEED'] = int(config['SEED'])
        except ValueError:
            raise ValueError("SEED must be an integer")
    else:
        config['SEED'] = int(time.time() * 1000)
    if 'ALGORITHM' in config:
        config['ALGORITHM'] = config['ALGORITHM']
    else:
        config['ALGORITHM'] = "backtracker"
    return config


if __name__ == "__main__":
    try:
        # 1. Initial Setup
        config = parse_config(sys.argv[1])
        # Assume generator is your logic class

        while True:
            # 2. Logic: Generate & Solve
            grid = Grid(config['WIDTH'], config['HEIGHT'])
            viz = ConsoleVisualizer(grid, config['ENTRY'],
                                    config['EXIT'])
            generator = MazeGenerator(grid, config['WIDTH'], config['HEIGHT'],
                                      viz, config['SEED'], config['ALGORITHM'])
            generator.generate()
            # solution_path = generator.solve(config['ENTRY'], config['EXIT'])
            solution_path = "--"

            # 3. Save to File (Mandatory)
            save_maze(grid, config['ENTRY'], config['EXIT'],
                      solution_path, config['OUTPUT_FILE'])

            # 4. Initialize Visualizer
            viz.set_path(solution_path)

            # 5. Interaction Loop [cite: 192]
            while True:
                viz.render()
                print("\n=== A-Maze-ing Menu ===")
                print("1. Re-generate new maze")
                print(f"2. {'Hide' if viz.show_path else 'Show'} path")
                print("3. Rotate colors")
                print("4. change algorithm")
                print("q. Quit")

                choice = input("Choice? (1-4): ").strip()

                if choice == '1':
                    break  # Break inner loop to regenerate
                elif choice == '2':
                    viz.show_path = not viz.show_path
                elif choice == '3':
                    viz.color_idx = (viz.color_idx + 1) % len(COLORS)
                elif choice == '4':
                    while True:
                        try:
                            i = int(input("Enter algorithm: "))
                        except ValueError:
                            continue
                        new_algorithm = ["backtracker", "kruskal"][i % 2]
                        break
                    config['ALGORITHM'] = new_algorithm
                elif choice == 'q':
                    print("Goodbye!")
                    sys.exit(0)
                else:
                    print("Invalid choice.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
