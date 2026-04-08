from mazegen.grid import Grid


def save_maze(grid: Grid, entry: tuple[int, int], exit: tuple[int, int],
              path: str, filename: str) -> None:
    """Save the generated maze, its endpoints, and the solution path to a file.

    Iterates through the maze grid and writes its integer values as hexadecimal
    characters to represent the maze body. It appends the entry coordinates,
    exit coordinates, and the solution path string at the end of the file.

    Args:
        grid (Grid): The generated maze grid object to save.
        entry (tuple[int, int]): The (x, y) coordinates of the maze entry.
        exit (tuple[int, int]): The (x, y) coordinates of the maze exit.
        path (str): The directional string representing the solution path.
        filename (str): The destination file path where the data will
            be written.
    """
    if not isinstance(grid, Grid):
        raise TypeError(f"Expected Grid for grid, got {type(grid).__name__}")
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
    if not isinstance(path, str):
        raise TypeError(f"Expected str for path, got {type(path).__name__}")
    if not isinstance(filename, str):
        raise TypeError(f"Expected str for filename, "
                        f"got {type(filename).__name__}")
    if not filename.strip():
        raise ValueError("filename cannot be an empty string")

    hex_chars = "0123456789ABCDEF"

    with open(filename, 'w') as f:
        # 1. Write the Maze Body
        for y in range(grid.height):
            row_hex = []
            for x in range(grid.width):
                val = grid.get_value(x, y)
                row_hex.append(hex_chars[val])
            f.write("".join(row_hex) + "\n")

        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write(f"{path}\n")


def cell_42(width: int, height: int) -> set[tuple[int, int]]:
    """Generate a set of coordinates representing a centered '42' shape.

    Creates a predefined shape of the number '42' and calculates its placement
    to perfectly center it within a grid of the provided width and
    height.

    Args:
        width (int): The total width of the maze grid.
        height (int): The total height of the maze grid.

    Returns:
        set[tuple[int, int]]: A set of (x, y) coordinates forming
            the '42' shape.

    Raises:
        ValueError: If the grid dimensions are too small to fit the '42'
            imprint.
    """
    if not isinstance(width, int):
        raise TypeError(f"Expected int for width, got {type(width).__name__}")
    if width <= 0:
        raise ValueError("width must be a positive integer")
    if not isinstance(height, int):
        raise TypeError("Expected int for height, "
                        f"got {type(height).__name__}")
    if height <= 0:
        raise ValueError("height must be a positive integer")

    cells = set()
    shape = [
        "1   111",
        "1     1",
        "111 111",
        "  1 1  ",
        "  1 111"
    ]

    shape_h = len(shape)
    shape_w = len(shape[0])

    if width < shape_w + 2 or height < shape_h + 2:
        raise ValueError("Grid too small for imprinting 42")

    start_x = (width - shape_w) // 2
    start_y = (height - shape_h) // 2

    for y, row in enumerate(shape):
        for x, char in enumerate(row):
            if char == '1':
                cells.add((start_x + x, start_y + y))
    return cells
