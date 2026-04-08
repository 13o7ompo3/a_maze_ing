class Grid:
    """Represent the maze grid and its internal cell states.

    The grid is represented as a 1D list of integers, where each integer acts
    as a bitmask for the walls (North=1, East=2, South=4, West=8). By default,
    all cells are initialized with all walls intact (value 15).
    """

    def __init__(self, width: int, height: int):
        """Initialize the Grid with the specified width and height.

        Args:
            width (int): The total width (number of columns) of the grid.
            height (int): The total height (number of rows) of the grid.
        """
        if not isinstance(width, int):
            raise TypeError("Expected int for width, "
                            f"got {type(width).__name__}")
        if width <= 0:
            raise ValueError("width must be a positive integer")
        if not isinstance(height, int):
            raise TypeError("Expected int for height, "
                            f"got {type(height).__name__}")
        if height <= 0:
            raise ValueError("height must be a positive integer")
        self.width = width
        self.height = height
        self.cells = [15] * (width * height)

    def get_index(self, x: int, y: int) -> int:
        """Calculate the 1D list index for a given 2D (x, y) coordinate.

        Args:
            x (int): The x-coordinate (column) of the cell.
            y (int): The y-coordinate (row) of the cell.

        Returns:
            int: The corresponding index in the 1D cells list.
        """
        if not isinstance(x, int):
            raise TypeError(f"Expected int for x, got {type(x).__name__}")
        if not isinstance(y, int):
            raise TypeError(f"Expected int for y, got {type(y).__name__}")
        if not (0 <= x < self.width):
            raise ValueError(f"x coordinate {x} is out of bounds "
                             f"for width {self.width}")
        if not (0 <= y < self.height):
            raise ValueError(f"y coordinate {y} is out of bounds "
                             f"for height {self.height}")
        return y * self.width + x

    def get_value(self, x: int, y: int) -> int:
        """Retrieve the bitmask value of the cell at the given coordinates.

        Args:
            x (int): The x-coordinate (column) of the cell.
            y (int): The y-coordinate (row) of the cell.

        Returns:
            int: The bitmask integer representing the walls of the cell.
        """
        if not isinstance(x, int):
            raise TypeError(f"Expected int for x, got {type(x).__name__}")
        if not isinstance(y, int):
            raise TypeError(f"Expected int for y, got {type(y).__name__}")
        if not (0 <= x < self.width):
            raise ValueError(f"x coordinate {x} is out of bounds "
                             f"for width {self.width}")
        if not (0 <= y < self.height):
            raise ValueError(f"y coordinate {y} is out of bounds "
                             f"for height {self.height}")
        return self.cells[self.get_index(x, y)]

    def remove_wall(self, x: int, y: int, direction: int) -> None:
        """Remove a specific wall from the cell at the given coordinates.

        Args:
            x (int): The x-coordinate (column) of the cell.
            y (int): The y-coordinate (row) of the cell.
            direction (int): The bitmask value of the wall to remove
                (1=N, 2=E, 4=S, 8=W).
        """
        if not isinstance(x, int):
            raise TypeError(f"Expected int for x, got {type(x).__name__}")
        if not isinstance(y, int):
            raise TypeError(f"Expected int for y, got {type(y).__name__}")
        if not isinstance(direction, int):
            raise TypeError(f"Expected int for direction, "
                            f"got {type(direction).__name__}")
        if direction not in {1, 2, 4, 8}:
            raise ValueError(
                f"Invalid direction bitmask: {direction}. "
                "Expected one of {1, 2, 4, 8}.")
        idx = self.get_index(x, y)
        self.cells[idx] &= ~direction  # Turn off the bit
