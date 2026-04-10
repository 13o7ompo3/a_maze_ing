from .base import SolverStrategy
from time import sleep


class DFSSolver(SolverStrategy):
    """Implement the Depth-First Search (DFS) algorithm for solving mazes.

    Inherits from SolverStrategy and uses a stack-based approach to
    deeply explore paths before backtracking to find a route from
    the entry to the exit.
    """

    def solve(self) -> str:
        """Solve the maze using Depth-First Search.

        Explores the maze grid starting from the entry point, pushing
        valid moves onto a stack. If visualization is enabled, it updates
        the visualizer to show the exploration path.

        Returns:
            str: A string of directional characters ('N', 'S', 'E', 'W')
                representing the path from entry to exit. Returns an
                empty string if no path is found.
        """
        stack = [(*self.entry, "")]
        visited = {self.entry}

        while stack:
            x, y, path = stack.pop()

            if (x, y) == self.exit:
                return path

            current_val = self.grid.get_value(x, y)

            moves = [('N', 0, -1, 1),
                     ('S', 0, 1, 4),
                     ('E', 1, 0, 2),
                     ('W', -1, 0, 8)]

            for move_char, dx, dy, bit in moves:
                nx, ny = x + dx, y + dy

                if not (0 <= nx < self.grid.width and
                        0 <= ny < self.grid.height):
                    continue
                if (current_val & bit) == 0:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        stack.append((nx, ny, path + move_char))
                        if self.viz and self.vizualize and self.viz.show_path:
                            sleep(0.03)
                            old_path_coords = self.viz.path_coords.copy()
                            self.viz.set_path(path + move_char)
                            for cx, cy in (old_path_coords |
                                           self.viz.path_coords):
                                self.viz.render_cells(cx, cy)
        return ""
