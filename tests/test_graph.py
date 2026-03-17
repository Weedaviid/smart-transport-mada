import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "source")
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

from graph import Graph


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.g = Graph()
        self.g.add_node("A", latitude=-18.9, longitude=47.5)
        self.g.add_node("B", latitude=-18.8, longitude=47.6)
        self.g.add_node("C", latitude=-18.7, longitude=47.7)

    def test_add_edge_and_neighbors(self):
        self.g.add_edge("A", "B", distance=1.2, duration=3, price=5000, transport_types=["taxi"])

        a = self.g.get_node("A")
        neighbors = a.get_neighbors()

        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]["node"].name, "B")
        self.assertEqual(neighbors[0]["distance"], 1.2)
        self.assertEqual(neighbors[0]["duration"], 3)
        self.assertEqual(neighbors[0]["price"], 5000)

    def test_add_edge_raises_for_missing_node(self):
        with self.assertRaises(ValueError):
            self.g.add_edge("A", "Z", distance=1.0, duration=2, price=1000, transport_types=["taxi"])

    def test_get_path_info(self):
        self.g.add_edge("A", "B", distance=1.0, duration=4, price=100, transport_types=["taxi"])
        self.g.add_edge("B", "C", distance=2.0, duration=6, price=200, transport_types=["taxi"])

        path = [self.g.get_node("A"), self.g.get_node("B"), self.g.get_node("C")]
        info = self.g.get_path_info(path)

        self.assertEqual(info["distance"], 3.0)
        self.assertEqual(info["duration"], 10)
        self.assertEqual(info["price"], 300)


if __name__ == "__main__":
    unittest.main()
