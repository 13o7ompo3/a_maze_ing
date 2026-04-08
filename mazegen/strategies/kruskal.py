from mazegen.strategies.base import GenerationStrategy
from mazegen.visualizer import ConsoleVisualizer
from mazegen.grid import Grid
from random import Random
from time import sleep


class DisjointSet:
    """Represent a disjoint-set (Union-Find) data structure.

    This structure tracks a set of elements partitioned into a number of
    disjoint (non-overlapping) subsets. It provides near-constant time
    operations to merge existing sets and determine whether elements are
    in the same set.
    """

    def __init__(self, size: int) -> None:
        """Initialize the DisjointSet with a given number of elements.

        Args:
            size (int): The total number of disjoint elements to track.
        """
        if not isinstance(size, int):
            raise TypeError("Expected int for size, "
                            f"got {type(size).__name__}")
        if size < 0:
            raise ValueError("size cannot be negative")
        self.parent = list(range(size))

    def find(self, i: int) -> int:
        """Find the representative (root) of the set containing the element i.

        Uses path compression to flatten the structure of the tree, ensuring
        that subsequent lookups are significantly faster.

        Args:
            i (int): The element to find the root for.

        Returns:
            int: The root identifier of the set containing element i.
        """
        if not isinstance(i, int):
            raise TypeError(f"Expected int for i, got {type(i).__name__}")
        if i < 0 or i >= len(self.parent):
            raise ValueError(f"Index i ({i}) is out of bounds for DisjointSet")
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int) -> bool:
        """Merge the sets containing elements i and j.

        Args:
            i (int): The first element.
            j (int): The second element.

        Returns:
            bool: True if the sets were successfully merged, False if
                they were already in the same set.
        """
        if not isinstance(i, int):
            raise TypeError(f"Expected int for i, got {type(i).__name__}")
        if not isinstance(j, int):
            raise TypeError(f"Expected int for j, got {type(j).__name__}")
        if i < 0 or i >= len(self.parent):
            raise ValueError(f"Index i ({i}) is out of bounds for DisjointSet")
        if j < 0 or j >= len(self.parent):
            raise ValueError(f"Index j ({j}) is out of bounds for DisjointSet")
        root_i = self.find(i)
        root_j = self.find(j)

        if root_i != root_j:
            self.parent[root_i] = root_j
            return True
        return False


class Kruskal(GenerationStrategy):
    """Implement Kruskal's algorithm for maze generation.

    Treats the maze grid as a graph where cells are nodes and walls are edges.
    It randomly removes walls (edges) connecting disjoint sets of cells
    until all reachable cells belong to a single connected set.
    """

    def __init__(self, grid: Grid, rng: Random,
                 viz: ConsoleVisualizer | None = None,
                 shape: set[tuple[int, int]] | None = None,
                 perfect: bool = True,
                 vizualize: bool = True) -> None:
        """Initialize the Kruskal generation strategy.

        Args:
            grid (Grid): The maze grid object to be populated.
            rng (Random): The random number generator instance.
            viz (ConsoleVisualizer | None, optional): The visualizer object
                for rendering. Defaults to None.
            shape (set[tuple[int, int]] | None, optional): Coordinates
                to exclude from path generation. Defaults to None.
            perfect (bool, optional): Whether to generate a perfect
                maze (no loops). Defaults to True.
            vizualize (bool, optional): Whether to enable visualization.
                Defaults to True.
        """
        super().__init__(grid, rng, viz, perfect, vizualize)
        if shape is not None:
            if not isinstance(shape, set):
                raise TypeError("Expected set or None for shape, "
                                f"got {type(shape).__name__}")
            for item in shape:
                if (not isinstance(item, tuple) or len(item) != 2 or
                        not isinstance(item[0], int) or
                        not isinstance(item[1], int)):
                    raise TypeError("Expected set of tuples of two integers "
                                    "for shape")
        self.disjoint_set = DisjointSet(grid.width * grid.height)
        self.shape = shape

    def apply(self) -> None:
        """Apply Kruskal's algorithm to generate the maze.

        Compiles a list of all internal walls (edges), shuffles them, and
        iterates through the list. If removing a wall connects two previously
        disconnected areas (verified via the DisjointSet), the wall is removed.
        Edges that would create loops are saved as rejected edges, which can
        subsequently be used if an imperfect maze (with loops) is requested.
        """
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
            self.imperfect_maze(rejected_edges)
