*This project has been created as part of the 42 curriculum by obahya, tel-atou.*

# A-Maze-ing

## Description
**A-Maze-ing** is a comprehensive Python-based maze generator, solver, and visualizer. The main goal of this project is to parse user-defined configurations to programmatically generate valid mazes (both perfect and imperfect), solve them using graph traversal algorithms, and visualize the entire process in real-time within the terminal.

At its core, the program represents a maze as a 1D array using bitwise logic to map cell walls, applying mathematical algorithms to carve out paths from a solid block of grid cells. It features an interactive, animated console interface, allowing users to watch the algorithms work step-by-step or even navigate the maze themselves.

---

## Instructions (Installation & Execution)

### Prerequisites
**Python 3.10+** is required to run this project.

### Setup & Makefile Commands
The project is bundled with a `Makefile` to streamline the setup, linting, and execution processes.

* `make venv`: Creates a Python virtual environment (`.venv`) and installs the necessary dependencies.
* `make install`: Installs the required dependencies listed in `requirements.txt` into your current environment.
* `make run`: Executes the main program using the default `config.txt` file.
* `make debug`: Runs the program using the `pdb` debugger for troubleshooting.
* `make lint`: Runs `flake8` and `mypy` to check for style errors and type hints (with basic strictness).
* `make lint-strict`: Runs `flake8` and `mypy` in strict mode to ensure maximum code quality and type safety.
* `make clean`: Removes Python cache directories (`__pycache__`, `.pytest_cache`, `.mypy_cache`), compiled `.pyc` files, and build artifacts.
* `make deep-clean`: Performs a standard clean and also removes the `.venv` virtual environment.
* `make build`: Generates a reusable Python package (`.whl` and `.tar.gz`) in the `dist/` directory.

### Execution
To manually run the program with a specific configuration file:

    python3 a_maze_ing.py config.txt

---

## Configuration File Format

The program reads a configuration file formatted as `KEY=VALUE` pairs. Empty lines and lines starting with `#` are treated as comments and ignored.

### Mandatory Keys
* **WIDTH**: The number of columns in the maze grid (positive integer).
* **HEIGHT**: The number of rows in the maze grid (positive integer).
* **ENTRY**: The starting coordinates of the maze, formatted as `x,y` (e.g., `0,0`).
* **EXIT**: The ending coordinates of the maze, formatted as `x,y` (e.g., `49,49`).
* **OUTPUT_FILE**: The path where the generated maze data and solution will be saved.
* **PERFECT**: Boolean (`True`/`False`). If `True`, generates a maze with no loops (exactly one path between any two points). If `False`, generates an imperfect maze with multiple possible paths.

### Custom / Bonus Keys
* **SEED**: An optional string or integer to seed the random number generator, ensuring reproducible mazes.
* **ALGORITHM**: The maze generation algorithm to use. Options: `kruskal` or `backtracker`.
* **STRATEGY**: The maze solving algorithm to use. Options: `bfs` or `dfs`.
* **VIZUALIZE**: Boolean (`True`/`False`). Enables or disables the real-time terminal animation of the algorithms.

### Example `config.txt`:

    # Maze Dimensions
    WIDTH=50
    HEIGHT=50
    
    # Endpoints
    ENTRY=0,0
    EXIT=49,49
    
    # File Output
    OUTPUT_FILE=maze.txt
    
    # Generation and Solving Settings
    PERFECT=False
    ALGORITHM=kruskal
    STRATEGY=dfs
    SEED=42_school
    
    # Visuals
    VIZUALIZE=True

---

## Algorithm & Technical Choices

### Maze Generation Algorithms
* **Kruskal's Algorithm:** We implemented randomized Kruskal's algorithm utilizing a **Disjoint Set (Union-Find)** data structure. This algorithm was chosen because it produces highly unbiased, natural-looking spanning trees with many short dead ends. It treats the grid as a graph where cells are nodes and walls are edges, randomly removing walls between disjoint sets until the whole grid is connected.
* **Recursive Backtracker:** We chose the backtracker for its distinct style: it creates long, deep, and winding paths with fewer dead ends compared to Kruskal's. Crucially, **we converted the recursive logic into an iterative stack**. Python has strict recursion limits; by using an iterative stack, our program can generate massive grid sizes (e.g., 500x500) without crashing from a `RecursionError`.

### Braid Logic (Imperfect Mazes)
To support `PERFECT=False`, we implemented a "Braid" logic step (Algorithm 2). After a perfect maze is generated, we compile a list of rejected walls (edges that would have created loops). We randomly select a percentage of these walls and remove them. This eliminates dead ends and creates multiple valid routes to the exit.

### Bitwise Operations & 2x2 Room Prevention
The entire grid is represented as a 1D array of integers. We use bitwise logic to represent walls (North=1, East=2, South=4, West=8). A fully walled cell has a value of `15`. To remove a North wall, we simply apply a bitwise AND NOT (`val &= ~1`).

When creating imperfect mazes, removing random walls can inadvertently create 2x2 open rooms, which ruins the aesthetic and structure of a traditional maze. We implemented mathematical bitwise checks across adjacent cells to predict and prevent the removal of any wall that would result in a 2x2 open space.

---

## Reusable Module (`mazegen`)

The core architecture of A-Maze-ing has been designed as a modular, standalone Python package named `mazegen`. This allows other developers to easily integrate our maze generation and solving logic into their own projects.

**Installation:** Run `make build` to generate the Python package wheels.

    pip install dist/mazegen-*.whl

**Usage Example:**

    from mazegen.grid import Grid
    from mazegen.generator import MazeGenerator
    
    # Initialize a 50x50 grid
    grid = Grid(50, 50)
    
    # Create a generator with custom parameters (Kruskal, seed='42', perfect=True)
    generator = MazeGenerator(
        grid=grid, 
        width=50, 
        height=50, 
        seed="42", 
        algorithm_name="kruskal",
        perfect=True,
        vizualize=False
    )
    
    # Generate the maze
    generator.generate()
    
    # Access the raw bitwise integer values of the cells
    top_left_cell_value = grid.get_value(0, 0)

---

## Team & Project Management

### Roles
* **obahya:** Focused on the core mathematical logic, graph theory implementation (Disjoint Sets, DFS/BFS logic), bitwise cell operations, and optimizing the algorithms (converting recursion to iterative stacks).
* **tel-atou:** Handled the project's architecture, robust input parsing, Python packaging, and the main application loop.

### Planning & Evolution
We initially anticipated building the visualizer *after* perfecting the core algorithms. However, we quickly realized that debugging raw integer arrays was nearly impossible. We pivoted to build the `ConsoleVisualizer` first, which allowed us to visually debug our Kruskal's and Backtracker implementations in real-time.

### Pros & Cons
* **What Worked Well:** The modular design pattern (abstract base classes for `GenerationStrategy` and `SolverStrategy`) made it incredibly easy to swap out algorithms and add new features without breaking existing code. The iterative DFS approach completely solved our large-grid crashing issues.
* **What Could Be Improved:** The console rendering relies on ANSI escape codes to jump the cursor around the terminal. While visually impressive, rendering massive mazes (e.g., 100x100+) is bottlenecked by standard terminal string flushing speeds. Future iterations could use `curses` or a dedicated GUI library like `pygame` for faster rendering.

### Tools Used
* **Linting & Typing:** `flake8` (style enforcement) and `mypy` (static type checking).
* **Version Control:** Git & GitHub.

---

## Resources

### Standard Resources
* **Wikipedia:** Reference for Kruskal's algorithm and Union-Find data structures.
* **Python Docs:** Reference for `termios` and `tty` for real-time keypress detection.

### Explicit AI Usage Declaration
* **Optimization:** Providing insights on effectively refactoring the Recursive Backtracker from a standard recursive function into a while-loop using an iterative stack.
* **Code Quality:** Generating and validating Google-style PEP 257 compliant docstrings across the codebase, and offering automated diffs to resolve strict `flake8` line-length (E501) and trailing whitespace errors.

---

## Bonus Features
Our team went above and beyond the standard requirements by implementing the following bonus features:

* **Real-time Visualization:** The generation and solving processes are animated directly in the terminal, allowing users to watch the algorithms carve paths and explore dead ends in real-time.
* **Color Themes:** Users can press `3` in the main menu to dynamically cycle through various ANSI color themes for the maze walls and paths.
* **Interactive Player Mode:** Users can enter "Player Mode" to manually navigate the maze using the arrow keys. It includes a toggleable "Break Mode" to cheat and smash through walls.
* **Algorithm Toggling:** Switch between generation (Kruskal/Backtracker) and solving (BFS/DFS) algorithms on the fly from the terminal menu without restarting the program.
* **The "42" Imprint:** A dynamic shape of the number "42" is mathematically centered and imprinted as an impassable barrier inside the maze structure during generation, fully integrated into the collision and pathfinding logic.