"""The 2025 shortest-path algorithm of Duan, Mao, Mao, Shu and Yin [2].

The code follows the paper's pseudocode for Algorithm 1 (FindPivots), Algorithm 2
(BaseCase) and Algorithm 3 (BMSSP). Our variable names are longer than the
paper's single letters, so each docstring says which symbol each name stands
for. That should make it possible to read the code next to the pseudocode.

We simplified a few things (the README lists these too):
- The paper builds a custom data structure D. We use an ordinary heap instead.
- The paper first reshapes the graph so that every vertex has at most two edges
  in and two edges out. We skip that step.
- The paper assumes no two paths have the same length. We don't go that far:
  we compare vertices by the pair (distance, vertex number), so no two vertices
  tie, but two paths can. This only works when every edge weight is positive,
  because then each vertex sorts after the vertex just before it on its
  shortest path.
"""
import heapq
import math
from collections import Counter
from math import inf

from graphs import Graph

# Vertices are ordered by the pair (distance, vertex number). The paper's bounds
# are pairs of the same kind, and (inf, inf) works as a bound above every vertex.
OrderKey = tuple[float, float]


def duan(graph: Graph, source: int) -> list[float]:
    """Return the shortest distance from source to every vertex (inf if unreachable).

    Two numbers from the paper control the recursion. rounds is the paper's k. It
    sets how many Bellman-Ford rounds find_pivots runs, how big a tree has to be
    before its root counts as a pivot, and the most vertices base_case returns. doublings_per_level is the paper's t: each level up the
    recursion handles 2 ** doublings_per_level times as many vertices as the one
    below it.
    """
    n = len(graph)
    rounds = max(1, math.floor(math.log2(n) ** (1 / 3)))
    doublings_per_level = max(1, math.floor(math.log2(n) ** (2 / 3)))
    top_level = math.ceil(math.log2(n) / doublings_per_level)

    distance = [inf] * n  # best distance found so far, the paper's d̂[v]
    distance[source] = 0

    def order_key(v: int) -> tuple[float, int]:
        """Sort key for v. Vertices at the same distance are ordered by number."""
        return (distance[v], v)

    def find_pivots(bound: OrderKey, sources: set[int]) -> tuple[set[int], set[int]]:
        """Algorithm 1: run a few Bellman-Ford rounds out from the sources, staying below the bound.

        In the paper, bound is B and sources is S. Returns the pivots P, which are
        some of the sources, and the set W of every vertex reached on the way.
        """
        reached = set(sources)
        frontier = set(sources)  # vertices improved in the previous round, W_{i-1}
        for _ in range(rounds):
            next_frontier = set()  # vertices improved in this round, W_i
            for u in frontier:
                for v, weight in graph[u]:
                    if distance[u] + weight <= distance[v]:
                        distance[v] = distance[u] + weight
                        if order_key(v) < bound:
                            next_frontier.add(v)
            reached |= next_frontier
            frontier = next_frontier
            if len(reached) > rounds * len(sources):
                # W has more than k|S| vertices. The paper stops here and makes
                # every source a pivot.
                return sources, reached
        return big_tree_roots(sources, reached), reached

    def big_tree_roots(sources: set[int], reached: set[int]) -> set[int]:
        """Return the sources whose tree in the forest F has at least `rounds` vertices.

        F is made of the edges u -> v, with both ends in reached, that lie on a
        shortest path found so far (distance[u] + weight == distance[v]). When a
        vertex has several such incoming edges we keep only one as its parent,
        which is what makes F a forest. It doesn't matter which one we keep.
        Walking up the parents can't go in a circle, since weights are positive
        and every parent is strictly closer to the source.
        """
        parent = {}
        for u in reached:
            for v, weight in graph[u]:
                if v in reached and distance[u] + weight == distance[v]:
                    parent[v] = u
        tree_size = Counter()
        for v in reached:
            root = v
            while root in parent:
                root = parent[root]
            tree_size[root] += 1
        return {u for u in sources if tree_size[u] >= rounds}

    def base_case(bound: OrderKey, sources: set[int]) -> tuple[OrderKey, set[int]]:
        """Algorithm 2: run Dijkstra from the one source until rounds + 1 vertices are finished.

        In the paper, bound is B and sources is the one-vertex set S = {x}.
        Returns a new bound B' (at most B) and the set U of vertices finished
        below it.
        """
        [start] = sources
        finished = set()  # the paper's U_0
        heap = [order_key(start)]
        while heap and len(finished) < rounds + 1:
            popped_distance, u = heapq.heappop(heap)
            if u in finished or popped_distance > distance[u]:
                continue  # u is already done, or this entry is from an older, longer path
            finished.add(u)
            for v, weight in graph[u]:
                if distance[u] + weight <= distance[v] and (distance[u] + weight, v) < bound:
                    distance[v] = distance[u] + weight
                    heapq.heappush(heap, order_key(v))
        if len(finished) <= rounds:
            # Dijkstra ran out of vertices below B first, so B stays the bound.
            return bound, finished
        # We finished one vertex more than allowed. The largest one becomes the
        # new bound and is left out of U.
        new_bound = max(order_key(v) for v in finished)
        return new_bound, {v for v in finished if order_key(v) < new_bound}

    def bmssp(level: int, bound: OrderKey, sources: set[int]) -> tuple[OrderKey, set[int]]:
        """Algorithm 3: bounded multi-source shortest paths.

        Finishes every vertex below the bound whose shortest path goes through
        one of the sources. In the paper, bound is B and sources is S. Returns a
        new bound B' (at most B) and the set U of vertices finished below it. If
        B' comes back smaller than B, the call quit early because U got too big.

        Each time around the loop we pull a batch S_i out of D, along with its
        bound B_i, and recurse on it. The recursive call hands back
        batch_new_bound (B'_i) and batch_finished (U_i).
        """
        if level == 0:
            return base_case(bound, sources)
        pivots, reached = find_pivots(bound, sources)

        heap, queued_value = [], {}  # together these are D (see the helpers below)
        for pivot in pivots:
            insert_or_decrease(heap, queued_value, pivot, distance[pivot])
        batch_size = 2 ** ((level - 1) * doublings_per_level)  # the paper's M
        max_finished = rounds * 2 ** (level * doublings_per_level)  # k * 2^(level * t)

        batch_new_bound = bound  # if D starts out empty the loop never runs
        finished = set()
        while len(finished) < max_finished and queued_value:
            batch_bound, batch = pull_smallest(heap, queued_value, batch_size, bound)
            batch_new_bound, batch_finished = bmssp(level - 1, batch_bound, batch)
            finished |= batch_finished
            # The paper adds values below batch_bound with BatchPrepend instead
            # of Insert, because its D can do that faster. A heap has no faster
            # way, so we insert everything.
            for u in batch_finished:
                for v, weight in graph[u]:
                    if distance[u] + weight <= distance[v]:
                        distance[v] = distance[u] + weight
                        if batch_new_bound <= order_key(v) < bound:
                            insert_or_decrease(heap, queued_value, v, distance[v])
            for v in batch:
                if batch_new_bound <= order_key(v) < batch_bound:
                    insert_or_decrease(heap, queued_value, v, distance[v])

        new_bound = min(batch_new_bound, bound)
        # Vertices from find_pivots that ended up below the new bound are done too.
        finished |= {v for v in reached if order_key(v) < new_bound}
        return new_bound, finished

    bmssp(top_level, (inf, inf), {source})
    return distance


# Our stand-in for the paper's data structure D is a heap of (value, vertex)
# entries plus a dict holding each vertex's current value in D. Lowering a
# value pushes a new entry and leaves the old one in the heap, so the heap can
# contain out-of-date entries. An entry is out of date when it doesn't match the
# dict, and we throw those away as they reach the top.


def insert_or_decrease(
    heap: list[tuple[float, int]], queued_value: dict[int, float], v: int, value: float
) -> None:
    """Add v to D with the given value. If v is already in D, only ever lower its value."""
    if value < queued_value.get(v, inf):
        queued_value[v] = value
        heapq.heappush(heap, (value, v))


def pull_smallest(
    heap: list[tuple[float, int]], queued_value: dict[int, float], batch_size: int,
    bound: OrderKey,
) -> tuple[OrderKey, set[int]]:
    """Take up to batch_size vertices with the smallest values out of D.

    Returns a bound for the batch along with the batch itself. The bound is the
    smallest entry still in D, which is above everything we took out. If D is
    empty afterwards, the bound is just the bound passed in.
    """
    batch = set()
    drop_stale_entries(heap, queued_value)
    while queued_value and len(batch) < batch_size:
        _, v = heapq.heappop(heap)
        del queued_value[v]
        batch.add(v)
        drop_stale_entries(heap, queued_value)
    batch_bound = heap[0] if queued_value else bound
    return batch_bound, batch


def drop_stale_entries(heap: list[tuple[float, int]], queued_value: dict[int, float]) -> None:
    """Pop out-of-date entries off the top of the heap until the top one is current."""
    while heap and queued_value.get(heap[0][1]) != heap[0][0]:
        heapq.heappop(heap)
