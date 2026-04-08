from mazegen.grid import Grid


def save_maze(grid: Grid, entry: tuple[int, int], exit: tuple[int, int],
              path: str, filename: str) -> None:
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
