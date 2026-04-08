from mazegen.strategies.base import GenerationStrategy
from mazegen.visualizer import ConsoleVisualizer
from mazegen.grid import Grid
from random import Random
from time import sleep


class DisjointSet:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, i: int) -> int:
        """Find the representative (root) of the set containing i"""
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int) -> bool:
        """Merge the sets containing i and j"""
        root_i = self.find(i)
        root_j = self.find(j)

        if root_i != root_j:
            self.parent[root_i] = root_j
            return True
        return False


class Kruskal(GenerationStrategy):
    def __init__(self, grid: Grid, rng: Random,
                 viz: ConsoleVisualizer | None = None,
                 shape: set[tuple[int, int]] | None = None,
                 perfect: bool = True,
                 vizualize: bool = True) -> None:
        super().__init__(grid, rng, viz, perfect, vizualize)
        self.disjoint_set = DisjointSet(grid.width * grid.height)
        self.shape = shape

    def apply(self) -> None:
        w, h = self.grid.width, self.grid.height
        ds = self.disjoint_set
        edges = []
        rejected_edges = []

        for y in range(h):
            for x in range(w):
                if x < w - 1:
                    edges.append(((x, y), (x + 1, y), 2, 8))
                if y < h - 1:
                    edges.append(((x, y), (x, y + 1), 4, 1))

        self.rng.shuffle(edges)

        for cell_a, cell_b, wall_a, wall_b in edges:
            idx_a = self.grid.get_index(*cell_a)
            idx_b = self.grid.get_index(*cell_b)

            if self.shape and (cell_a in self.shape or cell_b in self.shape):
                continue

            if ds.union(idx_a, idx_b):
                self.grid.remove_wall(cell_a[0], cell_a[1], wall_a)
                self.grid.remove_wall(cell_b[0], cell_b[1], wall_b)
                if self.viz and self.vizualize:
                    sleep(0.04)
                    self.viz.render_cells(cell_a[0], cell_a[1])
                    self.viz.render_cells(cell_b[0], cell_b[1])
            else:
                rejected_edges.append((cell_a, cell_b, wall_a, wall_b))

        if not self.perfect:
            p_c = 0.05
            k = int(p_c * ((w * h) - w - h + 1))
            self.rng.shuffle(rejected_edges)

            for cell_a, cell_b, wall_a, wall_b in rejected_edges:
                if k <= 0:
                    break

                x, y = cell_a
                nx, ny = cell_b

                if not self._creates_2x2_room(x, y, nx, ny, wall_a):

                    self.grid.remove_wall(x, y, wall_a)
                    self.grid.remove_wall(nx, ny, wall_b)
                    k -= 1

                    if self.viz and self.vizualize:
                        sleep(0.04)
                        self.viz.render_cells(x, y)
                        self.viz.render_cells(nx, ny)
