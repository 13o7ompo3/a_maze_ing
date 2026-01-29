from mazegen.strategies.base import GenerationStrategy
from mazegen.visualizer import ConsoleVisualizer
from mazegen.grid import Grid
from random import Random
from time import sleep


class DisjointSet:
    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, i):
        """Find the representative (root) of the set containing i"""
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        """Merge the sets containing i and j"""
        root_i = self.find(i)
        root_j = self.find(j)

        if root_i != root_j:
            self.parent[root_i] = root_j
            return True
        return False


class Kruskal(GenerationStrategy):
    def __init__(self, grid: Grid, rng: Random, cells_42: set,
                 viz: ConsoleVisualizer):
        super().__init__(grid, rng, cells_42, viz)
        self.disjoint_set = DisjointSet(grid.width * grid.height)

    def apply(self):
        w, h = self.grid.width, self.grid.height
        ds = self.disjoint_set
        edges = []

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

            if cell_a in self.cells_42 or cell_b in self.cells_42:
                continue

            if ds.find(idx_a) != ds.find(idx_b):
                ds.union(idx_a, idx_b)
                self.grid.remove_wall(cell_a[0], cell_a[1], wall_a)
                self.grid.remove_wall(cell_b[0], cell_b[1], wall_b)
                sleep(0.01)
                self.viz.render()
