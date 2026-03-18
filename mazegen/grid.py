class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells = [15] * (width * height)

    def get_index(self, x: int, y: int) -> int:
        return y * self.width + x

    def get_value(self, x: int, y: int) -> int:
        return self.cells[self.get_index(x, y)]

    def remove_wall(self, x: int, y: int, direction: int):
        # direction: 1=N, 2=E, 4=S, 8=W
        idx = self.get_index(x, y)
        self.cells[idx] &= ~direction  # Turn off the bit
