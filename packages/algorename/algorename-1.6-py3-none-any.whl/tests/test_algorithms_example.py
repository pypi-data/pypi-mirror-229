import unittest
from algorithms.example import apply_algorithm as apply_algorithm_example
from algorithms.example2 import apply_algorithm as apply_algorithm_example2


class TestAlgorithmsExample(unittest.TestCase):
    def test_example_algorithm(self):
        self.assertEqual(apply_algorithm_example("python"), "oxsgnm")
        self.assertEqual(apply_algorithm_example("Python"), "Oxsgnm")
        self.assertEqual(apply_algorithm_example("pythoN"), "oxsgnM")
    
    def test_example2_algorithm(self):
        self.assertEqual(apply_algorithm_example2("oxsgnm"), "python")
        self.assertEqual(apply_algorithm_example2("Oxsgnm"), "Python")
        self.assertEqual(apply_algorithm_example2("oxsgnM"), "pythoN")
