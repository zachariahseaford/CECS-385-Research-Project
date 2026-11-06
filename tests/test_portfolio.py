import unittest
import numpy as np
from scripts.portfolio import portfolio_score, exhaustive_search, greedy_search, demo_prices


class TestPortfolio(unittest.TestCase):
    def test_search_matches_bruteforce_small_case(self):
        mu = np.array([0.08, 0.12, 0.10, 0.04, 0.03])
        cov = np.eye(5) * 0.05
        exact, value, _ = exhaustive_search(mu, cov, choose=3)
        self.assertEqual(len(exact), 3)
        self.assertEqual(set(exact), {0, 1, 2})
        self.assertAlmostEqual(value, portfolio_score(exact, mu, cov))
        greedy, greedy_value, _ = greedy_search(mu, cov)
        self.assertLessEqual(greedy_value, value + 1e-10)
        self.assertEqual(len(greedy), 3)

    def test_demo_data(self):
        prices = demo_prices(n=6)
        self.assertEqual(prices.shape[1], 6)
        self.assertTrue((prices > 0).all().all())

if __name__ == '__main__':
    unittest.main()
