import os
import sys
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "source")
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

from graph import Graph
from dijkstra import dijkstra
from astar import astar


def build_grid_graph(size):
    g = Graph()

    # Add nodes
    for r in range(size):
        for c in range(size):
            name = f"N{r}_{c}"
            g.add_node(name, latitude=-18.9 + r * 0.001, longitude=47.5 + c * 0.001)

    # Add directed edges in 4-neighborhood (both directions)
    for r in range(size):
        for c in range(size):
            current = f"N{r}_{c}"
            neighbors = []
            if r + 1 < size:
                neighbors.append((r + 1, c))
            if c + 1 < size:
                neighbors.append((r, c + 1))
            if r - 1 >= 0:
                neighbors.append((r - 1, c))
            if c - 1 >= 0:
                neighbors.append((r, c - 1))

            for nr, nc in neighbors:
                target = f"N{nr}_{nc}"
                g.add_edge(current, target, distance=1.0, duration=2, price=50, transport_types=["taxi"])

    return g


class TestLoadAlgorithms(unittest.TestCase):
    def test_small_load_protocol(self):
        size = 16  # 256 nodes
        repetitions = 8
        start = "N0_0"
        end = f"N{size-1}_{size-1}"

        g = build_grid_graph(size)

        # Warm-up
        warm_a = astar(g, start, end, weight="distance")
        warm_d = dijkstra(g, start, end, weight="distance")
        self.assertTrue(warm_a["path"])
        self.assertTrue(warm_d["path"])

        astar_times = []
        dijkstra_times = []

        for _ in range(repetitions):
            t0 = time.perf_counter()
            ra = astar(g, start, end, weight="distance")
            t1 = time.perf_counter()
            rd = dijkstra(g, start, end, weight="distance")
            t2 = time.perf_counter()

            self.assertTrue(ra["path"])
            self.assertTrue(rd["path"])
            self.assertEqual(ra["distance"], rd["distance"])

            astar_times.append(t1 - t0)
            dijkstra_times.append(t2 - t1)

        avg_astar = sum(astar_times) / len(astar_times)
        avg_dijkstra = sum(dijkstra_times) / len(dijkstra_times)

        # Guardrail (avoid pathological regressions while keeping CI-friendly thresholds)
        self.assertLess(avg_astar, 2.0)
        self.assertLess(avg_dijkstra, 2.0)

        print(f"LOAD_TEST size={size} reps={repetitions} avg_astar={avg_astar:.4f}s avg_dijkstra={avg_dijkstra:.4f}s")


if __name__ == "__main__":
    unittest.main()
