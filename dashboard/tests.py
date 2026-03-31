from django.test import TestCase
from .algorithm import calculate_win_probability

class AlgorithmTest(TestCase):

    def test_easy_chase(self):
        result = calculate_win_probability(180, 140, 1, 80)
        self.assertGreater(result['batting_team'], 50)

    def test_tough_chase(self):
        result = calculate_win_probability(180, 100, 5, 90)
        self.assertLess(result['batting_team'], 30)

    def test_balanced_chase(self):
        result = calculate_win_probability(180, 120, 3, 60)
        self.assertAlmostEqual(result['batting_team'], 50, delta=15)

    def test_match_won(self):
        result = calculate_win_probability(180, 180, 3, 100)
        self.assertEqual(result['batting_team'], 100.0)

    def test_match_lost(self):
        result = calculate_win_probability(180, 100, 10, 120)
        self.assertEqual(result['batting_team'], 0.0)