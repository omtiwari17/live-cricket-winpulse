from django.test import TestCase
from .algorithm import calculate_win_probability, get_format_overs


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

    def test_first_innings_returns_none(self):
        result = calculate_win_probability(0, 120, 2, 70, first_innings=True)
        self.assertIsNone(result['batting_team'])
        self.assertIsNone(result['bowling_team'])

    def test_zero_target_returns_none(self):
        result = calculate_win_probability(0, 50, 1, 30)
        self.assertIsNone(result['batting_team'])
        self.assertIsNone(result['bowling_team'])

    def test_kwargs_tolerance(self):
        # Must not raise TypeError when called with unexpected kwargs (such as first_innings=(not match['target']))
        result = calculate_win_probability(
            target=180,
            runs=140,
            wickets=1,
            balls_bowled=80,
            total_overs=20,
            first_innings=False,
            legacy_flag=True,
            extra_param="unexpected"
        )
        self.assertIsNotNone(result['batting_team'])
        self.assertGreater(result['batting_team'], 50)

    def test_odi_chase_calculation(self):
        # In ODI (50 overs / 300 balls), 210 balls bowled leaves 90 balls.
        # Chasing 280 with 220/3 after 35 overs is a strong position.
        result = calculate_win_probability(
            target=280,
            runs=220,
            wickets=3,
            balls_bowled=210,
            total_overs=50
        )
        self.assertGreater(result['batting_team'], 50)

    def test_get_format_overs(self):
        self.assertEqual(get_format_overs("IPL"), 20)
        self.assertEqual(get_format_overs("T20 World Cup"), 20)
        self.assertEqual(get_format_overs("India T20I"), 20)
        self.assertEqual(get_format_overs("India ODI"), 50)
        self.assertEqual(get_format_overs("ODI World Cup"), 50)
        self.assertEqual(get_format_overs("Champions Trophy"), 50)
        self.assertEqual(get_format_overs("India Test"), 90)
        self.assertEqual(get_format_overs("WTC Final"), 90)
        self.assertEqual(get_format_overs("", "India tour of New Zealand 4th ODI 2026"), 50)
        self.assertEqual(get_format_overs("", "Border-Gavaskar Trophy 2nd Test"), 90)
