"""Portfolio-selection baselines for the CECS 385 ETF project."""
import itertools
import time
import numpy as np


def portfolio_score(indices, mu, covariance, risk_lambda=1.0, choose=3):
    """Annualized estimated return minus lambda * annualized variance."""
    w = np.zeros(len(mu), dtype=float)
    w[list(indices)] = 1.0 / choose
    return float(w @ mu - risk_lambda * (w @ covariance @ w))


def exhaustive_search(mu, covariance, risk_lambda=1.0, choose=3):
    start = time.perf_counter()
    best, best_score = None, float('-inf')
    for picked in itertools.combinations(range(len(mu)), choose):
        value = portfolio_score(picked, mu, covariance, risk_lambda, choose)
        if value > best_score:
            best, best_score = picked, value
    return best, best_score, time.perf_counter() - start


def greedy_search(mu, covariance, risk_lambda=1.0, choose=3):
    start = time.perf_counter()
    picked = []
    for _ in range(choose):
        candidates = [i for i in range(len(mu)) if i not in picked]
        next_index = max(candidates, key=lambda i: portfolio_score(picked + [i], mu, covariance, risk_lambda, choose))
        picked.append(next_index)
    return tuple(sorted(picked)), portfolio_score(picked, mu, covariance, risk_lambda, choose), time.perf_counter() - start


def demo_prices(n=12, seed=42, start='2015-01-01', end='2025-12-31'):
    """Generate synthetic test data. NEVER report as historical ETF evidence."""
    import pandas as pd
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, end)
    market = rng.normal(0.0002, 0.009, len(dates))
    data = {}
    for i in range(n):
        daily = market * rng.uniform(0.5, 1.2) + rng.normal(0.0001, rng.uniform(0.004, 0.013), len(dates))
        data[f'ETF{i+1:03d}'] = 100 * np.cumprod(1 + daily)
    return pd.DataFrame(data, index=dates)


def load_prices(path, tickers=None, start='2015-01-01', end='2025-12-31'):
    """Read wide adjusted-close CSV (Date and ticker columns)."""
    import pandas as pd
    prices = pd.read_csv(path, parse_dates=['Date']).set_index('Date').sort_index()
    prices = prices.loc[start:end]
    if tickers is not None:
        missing = [t for t in tickers if t not in prices.columns]
        if missing:
            raise ValueError(f'Missing ETF columns: {missing}')
        prices = prices[tickers]
    prices = prices.apply(pd.to_numeric, errors='coerce')
    if prices.empty or prices.isna().any().any() or (prices <= 0).any().any():
        raise ValueError('Missing/invalid prices. Check dates, ETF coverage and adjusted prices.')
    return prices
