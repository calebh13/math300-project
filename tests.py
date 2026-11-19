"""Check both algorithms on hand-solved graphs, then against each other on random graphs.

Run with: python tests.py
"""
import random
from math import inf

from dijkstra import dijkstra
from duan import duan
from graphs import random_graph

ALGORITHMS = [dijkstra, duan]


def test_small_graph() -> None:
    """0 -> 2 -> 1 -> 3 beats the direct edges. Vertex 4 cannot be reached."""
    graph = {
        0: [(1, 4), (2, 1)],
        1: [(3, 1)],
        2: [(1, 2), (3, 5)],
        3: [],
        4: [(0, 1)],
    }
    for algorithm in ALGORITHMS:
        assert algorithm(graph, 0) == [0, 3, 1, 4, inf]


def test_equal_distances() -> None:
    """Vertices 1 and 2 tie, and vertex 3 has two shortest paths."""
    graph = {
        0: [(1, 1), (2, 1)],
        1: [(3, 1)],
        2: [(3, 1)],
        3: [(4, 2)],
        4: [],
    }
    for algorithm in ALGORITHMS:
        assert algorithm(graph, 0) == [0, 1, 1, 2, 4]


def test_single_vertex() -> None:
    for algorithm in ALGORITHMS:
        assert algorithm({0: []}, 0) == [0]


def test_long_path() -> None:
    """A path 0 -> 1 -> ... -> 999 with weight 1 per edge, so dist[v] = v."""
    n = 1000
    graph = {u: [(u + 1, 1)] for u in range(n - 1)}
    graph[n - 1] = []
    for algorithm in ALGORITHMS:
        assert algorithm(graph, 0) == list(range(n))


def test_random_graphs_agree() -> None:
    random.seed(300)
    for n in [2, 3, 5, 10, 50, 100, 1000, 10000]:
        for edges_per_vertex in [1, 2, 4, 10]:
            graph = random_graph(n, edges_per_vertex * n)
            assert duan(graph, 0) == dijkstra(graph, 0), (n, edges_per_vertex)


if __name__ == "__main__":
    test_small_graph()
    test_equal_distances()
    test_single_vertex()
    test_long_path()
    test_random_graphs_agree()
    print("All tests passed.")
