import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "source")
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

from graph import Graph
from dijkstra import dijkstra
from astar import astar


class TestShortestPathAlgorithms(unittest.TestCase):
    def setUp(self):
        self.g = Graph()
        self.g.add_node("A", latitude=-18.90, longitude=47.50)
        self.g.add_node("B", latitude=-18.89, longitude=47.51)
        self.g.add_node("C", latitude=-18.88, longitude=47.52)
        self.g.add_node("D", latitude=-18.87, longitude=47.53)
        self.g.add_node("E", latitude=-18.86, longitude=47.54)  # disconnected

        # Path 1: A -> B -> D (best by distance)
        self.g.add_edge("A", "B", distance=1, duration=4, price=100, transport_types=["taxi"])
        self.g.add_edge("B", "D", distance=1, duration=4, price=100, transport_types=["taxi"])

        # Path 2: A -> C -> D (best by duration and price)
        self.g.add_edge("A", "C", distance=2, duration=1, price=20, transport_types=["moto-taxi"])
        self.g.add_edge("C", "D", distance=2, duration=1, price=20, transport_types=["moto-taxi"])

    def test_dijkstra_distance(self):
        result = dijkstra(self.g, "A", "D", weight="distance")
        path_names = [node.name for node in result["path"]]

        self.assertEqual(path_names, ["A", "B", "D"])
        self.assertEqual(result["distance"], 2)

    def test_dijkstra_duration(self):
        result = dijkstra(self.g, "A", "D", weight="duration")
        path_names = [node.name for node in result["path"]]

        self.assertEqual(path_names, ["A", "C", "D"])
        self.assertEqual(result["duration"], 2)

    def test_dijkstra_price(self):
        result = dijkstra(self.g, "A", "D", weight="price")
        path_names = [node.name for node in result["path"]]

        self.assertEqual(path_names, ["A", "C", "D"])
        self.assertEqual(result["price"], 40)

    def test_astar_distance(self):
        result = astar(self.g, "A", "D", weight="distance")
        path_names = [node.name for node in result["path"]]

        self.assertEqual(path_names, ["A", "B", "D"])

    def test_astar_duration(self):
        result = astar(self.g, "A", "D", weight="duration")
        path_names = [node.name for node in result["path"]]

        self.assertEqual(path_names, ["A", "C", "D"])

    def test_astar_price(self):
        result = astar(self.g, "A", "D", weight="price")
        path_names = [node.name for node in result["path"]]

        self.assertEqual(path_names, ["A", "C", "D"])

    def test_start_or_end_not_found(self):
        for algo in (dijkstra, astar):
            result = algo(self.g, "A", "Z", weight="distance")
            self.assertEqual(result["path"], [])
            self.assertIn("error", result)

    def test_no_path_found(self):
        for algo in (dijkstra, astar):
            result = algo(self.g, "A", "E", weight="distance")
            self.assertEqual(result["path"], [])
            self.assertIn("error", result)

    def test_start_equals_end(self):
        for algo in (dijkstra, astar):
            result = algo(self.g, "A", "A", weight="distance")
            self.assertEqual(len(result["path"]), 1)
            self.assertEqual(result["path"][0].name, "A")
            self.assertEqual(result["cost"], 0)

    def test_unknown_weight_fallback_to_distance(self):
        result = dijkstra(self.g, "A", "D", weight="unknown")
        path_names = [node.name for node in result["path"]]
        self.assertEqual(path_names, ["A", "B", "D"])


if __name__ == "__main__":
    unittest.main()
