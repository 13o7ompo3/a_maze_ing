from collections import deque
from time import sleep
from mazegen.strategies.base import SolverStrategy


class BFSSolver(SolverStrategy):
    """Implement the Breadth-First Search (BFS) algorithm for solving mazes.

    Inherits from SolverStrategy and uses a queue-based approach to explore
    the shortest path from the entry to the exit in an unweighted grid.
    """
    def solve(self) -> str:
        """Solve the maze using Breadth-First Search.

        Explores the maze grid starting from the entry point, enqueuing
        valid moves to find the shortest path. Updates the visualizer if
        visualization is enabled.

        Returns:
            str: A string of directional characters ('N', 'S', 'E', 'W')
                representing the path from entry to exit. Returns an
                empty string if no path is found.
        """
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
                        if self.viz and self.vizualize and self.viz.show_path:
                            sleep(0.03)
                            old_path_coords = self.viz.path_coords.copy()
                            self.viz.set_path(path + move_char)
                            for cx, cy in (old_path_coords |
                                           self.viz.path_coords):
                                self.viz.render_cells(cx, cy)
        return ""
