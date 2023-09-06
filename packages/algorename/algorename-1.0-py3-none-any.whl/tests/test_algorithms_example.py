import unittest
from algorithms.example import apply_algorithm


class TestAlgorithmsExample(unittest.TestCase):
    def test_example_algorithm(self):
        self.assertEqual(apply_algorithm("python"), "oxsgnm")
        self.assertEqual(apply_algorithm("Python"), "Oxsgnm")
        self.assertEqual(apply_algorithm("pythoN"), "oxsgnM")
