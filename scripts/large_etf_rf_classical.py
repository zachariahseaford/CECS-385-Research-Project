"""Classical baselines for 3/20, 6/40, 12/80 and 24/160 using REAL ETF prices.

Uses the same monthly Random Forest features, return-minus-variance objective
and January 2025 decision timing as Notebook 4. Exhaustive search only for
the tiny 3/20 problem; the larger ones use greedy plus one-swap improvement.
No optimality claim is made for greedy/local search on large groups.
"""
import itertools
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

OUT = Path("results/large_etf_feasibility")
MONTHLY = OUT / "new_data_source_monthly_prices.csv"
SCENARIOS = [(20, 3), (40, 6), (80, 12), (160, 24)]
LAMBDA = 1.0
SEED = 7


def score(indices, mu, cov, k):
    ids = np.asarray(indices, dtype=int)
    return float(mu[ids].sum() / k - LAMBDA * cov[np.ix_(ids, ids)].sum() / (k * k))


def greedy(mu, cov, k):
    chosen = []
    for _ in range(k):
        # Compare partial portfolios using the final k denominator (same objective).
        best = max((i for i in range(len(mu)) if i not in chosen),
                   key=lambda i: score(chosen + [i], mu, cov, k))
        chosen.append(best)
    return tuple(sorted(chosen))


def swap_gain(chosen, drop, add, mu, cov, k):
    left = [i for i in chosen if i != drop]
    delta_mu = (mu[add] - mu[drop]) / k
    delta_risk = ((cov[add, add] - cov[drop, drop]) +
                  2 * np.sum(cov[add, left] - cov[drop, left])) / (k * k)
    return float(delta_mu - LAMBDA * delta_risk)


def improve_by_swaps(mu, cov, chosen, k):
    chosen = tuple(sorted(chosen))
    steps = 0
    while True:
        inside = set(chosen)
        best_gain = 1e-12
        swap = None
        for drop in chosen:
            for add in range(len(mu)):
                if add in inside:
                    continue
                gain = swap_gain(chosen, drop, add, mu, cov, k)
                if gain > best_gain:
                    best_gain, swap = gain, (drop, add)
        if swap is None:
            break
        drop, add = swap
        chosen = tuple(sorted((inside - {drop}) | {add}))
        steps += 1
    return chosen, steps


def prepare_forecasts(monthly):
    names = []
    forecasts = []
    for t in monthly.columns:
        prices = monthly[t]
        if prices.loc["2020-01-31":"2024-12-31"].isna().any():
            continue
        r = prices.pct_change(fill_method=None)
        f = pd.DataFrame({
            "last_month": r,
            "last_3_months": prices.pct_change(3),
            "last_6_months": prices.pct_change(6),
            "volatility_3m": r.rolling(3).std(),
        })
        labeled = f.copy()
        labeled["next_month"] = r.shift(-1)
        train = labeled.loc[labeled.index <= "2024-11-30"].dropna()
        row = f.loc[["2024-12-31"]]
        if len(train) < 24 or row.isna().any().any():
            continue
        model = RandomForestRegressor(
            n_estimators=100, min_samples_leaf=3, random_state=SEED,
            n_jobs=1)
        model.fit(train[f.columns], train["next_month"])
        names.append(t)
        forecasts.append(float(model.predict(row)[0]))
    if not names:
        raise ValueError("No complete ETF series suitable for RF forecast")
    cov = monthly[names].pct_change(fill_method=None).loc[
        "2022-01-31":"2024-12-31"].cov().to_numpy()
    return names, np.asarray(forecasts), cov


def main():
    if not MONTHLY.exists():
        raise FileNotFoundError(MONTHLY)
    monthly = pd.read_csv(MONTHLY, index_col=0, parse_dates=True).sort_index()
    names, mu, cov = prepare_forecasts(monthly)
    print("ETF series with valid RF forecasts:", len(names), flush=True)
    results = []
    for n, k in SCENARIOS:
        if len(names) < n:
            print(f"SKIPPED {k}/{n}, only {len(names)} eligible RF series.", flush=True)
            continue
        u, c = mu[:n], cov[:n, :n]
        start = time.perf_counter()
        g = greedy(u, c, k)
        g_sec = time.perf_counter() - start
        start = time.perf_counter()
        improved, swaps = improve_by_swaps(u, c, g, k)
        swap_sec = time.perf_counter() - start
        assert len(g) == k and len(improved) == k
        assert score(improved, u, c, k) + 1e-10 >= score(g, u, c, k)
        row = {"etfs": n, "selected": k, "combination_count": str(math.comb(n, k)),
               "greedy_score": score(g, u, c, k), "greedy_seconds": g_sec,
               "swap_score": score(improved, u, c, k), "swap_seconds": swap_sec,
               "number_of_improving_swaps": swaps,
               "greedy_portfolio": ", ".join(names[i] for i in g),
               "improved_portfolio": ", ".join(names[i] for i in improved),
               "exact_optimum_known": False}
        if (n, k) == (20, 3):
            # Exact only in the original tractable-scale control experiment.
            start = time.perf_counter()
            exact = max(itertools.combinations(range(n), k),
                        key=lambda ids: score(ids, u, c, k))
            row["exact_score"] = score(exact, u, c, k)
            row["exact_seconds"] = time.perf_counter() - start
            row["exact_optimum_known"] = True
        results.append(row)
        print("COMPLETED", k, "/", n, row, flush=True)
    pd.DataFrame(results).to_csv(OUT / "expanded_rf_classical_results.csv", index=False)
    print("DONE: classical baselines only; QAOA for large scenarios not executed", flush=True)


if __name__ == "__main__":
    main()
