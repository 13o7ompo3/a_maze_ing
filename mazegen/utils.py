from mazegen.grid import Grid


def save_maze(grid: Grid, entry: tuple, exit: tuple, path: str, filename: str):
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
