"""Time Dijkstra and Duan et al. on bigger and bigger random graphs, then plot the times.

Run it with python benchmark.py. It takes a few minutes and saves the plot as runtime.png.
"""
import random
import time
from collections.abc import Callable

import matplotlib.pyplot as plt

from dijkstra import dijkstra
from duan import duan
from graphs import Graph, random_graph

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000, 300_000, 1_000_000]
EDGES_PER_VERTEX = 3
REPEATS = 3


def best_time(algorithm: Callable[[Graph, int], list[float]], graph: Graph) -> float:
    """Run the algorithm from vertex 0 REPEATS times and return the fastest time in seconds."""
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        algorithm(graph, 0)
        times.append(time.perf_counter() - start)
    return min(times)


def main() -> None:
    random.seed(300)
    dijkstra_times = []
    duan_times = []
    print(f"{'n':>10} {'Dijkstra (s)':>13} {'Duan et al. (s)':>16}")
    for n in SIZES:
        graph = random_graph(n, EDGES_PER_VERTEX * n)
        dijkstra_times.append(best_time(dijkstra, graph))
        duan_times.append(best_time(duan, graph))
        print(f"{n:>10} {dijkstra_times[-1]:>13.3f} {duan_times[-1]:>16.3f}")

    plt.rcParams["font.size"] = 14
    plt.figure(figsize=(7, 5))
    plt.loglog(SIZES, dijkstra_times, "o-", color="#2a78d6", linewidth=2, markersize=8,
               label="Dijkstra (1959)")
    plt.loglog(SIZES, duan_times, "s-", color="#eb6834", linewidth=2, markersize=8,
               label="Duan et al. (2025)")
    plt.xlabel("Number of vertices n")
    plt.ylabel("Running time (s)")
    plt.title(f"Random graphs with m = {EDGES_PER_VERTEX}n edges")
    plt.legend()
    plt.grid(True, which="major", color="#dddddd")
    plt.tight_layout()
    plt.savefig("runtime.png", dpi=200)


if __name__ == "__main__":
    main()
