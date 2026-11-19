# Finding Shortest Paths, Old and New

MATH300: Mathematical Computing, Fall 2026.

We implement and compare two algorithms for single-source shortest paths: Dijkstra's algorithm [1], using Python's `heapq` [3], and the 2025 algorithm of Duan et al. [2], which follows the paper's pseudocode. Compared to the paper, we made three simplifications:

- We use an ordinary heap instead of the paper's data structure D.
- We skip the step that limits every vertex to two incoming and two outgoing edges.
- Instead of assuming that all path lengths are different, we break ties by vertex number. This needs positive edge weights.

## Install and run

You need Python 3, and `matplotlib` for the benchmark (`pip install matplotlib`).

```
python tests.py       # checks both algorithms on hand-solved and random graphs
python benchmark.py   # times both algorithms and saves runtime.png (a few minutes)
```

We use an adjacency list for our graphs (in particular, a Python dict) with `graph[u] = [(v, weight), ...]` for every vertex `u` in `0..n-1`. Both algorithms return a list of distances from the source, with `math.inf` for vertices that can't be reached:

```python
from graphs import random_graph
from dijkstra import dijkstra
from duan import duan

graph = random_graph(1000, 3000)
assert dijkstra(graph, 0) == duan(graph, 0)
```

## Author contributions

| Part | Caleb Hansen | Michael | Lead |
|---|---:|---:|---|
| `graphs.py` (graph format, random graphs) | 10 % | 90 % | Michael |
| `dijkstra.py` (Dijkstra's algorithm) | 10 % | 90 % | Michael |
| `duan.py` (Duan et al.'s algorithm) | 90 % | 10 % | Caleb |
| `tests.py` (validation) | 90 % | 10 % | Caleb |
| `benchmark.py` (timing and plot) | 90 % | 10 % | Caleb |

## References

[1] E. W. Dijkstra (1959). A note on two problems in connexion with graphs. *Numerische Mathematik*, 1, 269–271. <https://doi.org/10.1007/BF01386390>

[2] R. Duan, J. Mao, X. Mao, X. Shu and L. Yin (2025). Breaking the sorting barrier for directed single-source shortest paths. arXiv:2504.17033. <https://arxiv.org/abs/2504.17033>

[3] Python Software Foundation. heapq — Heap queue algorithm, Python documentation. <https://docs.python.org/3/library/heapq.html>
