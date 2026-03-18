from collections import deque
from time import sleep
from mazegen.strategies.base import SolverStrategy


class BFSSolver(SolverStrategy):
    def solve(self) -> str:
        queue = deque([(self.entry[0], self.entry[1], "")])
        visited = {self.entry}

        while queue:
            x, y, path = queue.popleft()

            if (x, y) == self.exit:
                return path

            current_val = self.grid.get_value(x, y)

            moves = [
                ('N', 0, -1, 1),
                ('S', 0, 1, 4),
                ('E', 1, 0, 2),
                ('W', -1, 0, 8)
            ]

            for move_char, dx, dy, bit in moves:
                nx, ny = x + dx, y + dy

                if not (0 <= nx < self.grid.width and
                        0 <= ny < self.grid.height):
                    continue

                if (current_val & bit) == 0:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + move_char))
                        sleep(0.03)
                        self.viz.set_path(path + move_char)
                        self.viz.render()
        return ""
