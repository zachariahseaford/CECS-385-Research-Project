"""Check whether our historical price source can support 6/40, 12/80, 24/160.

The list is a *candidate ETF universe*, not a claim that every series is present.
Missing or incomplete prices are reported, not invented. This program does not
run large QAOA circuits; it audits data and benchmarks scalable classical search.
"""
from __future__ import annotations
import itertools
import math
import time
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE = "https://raw.githubusercontent.com/manisahni/marketdata/main/daily_adjclose.csv"
OUT = Path("results/large_etf_feasibility")
OUT.mkdir(parents=True, exist_ok=True)
SIZES = [(20, 3), (40, 6), (80, 12), (160, 24)]
# Candidate ETFs from several stock, bond, country, factor and commodity families.
# This is not a validated/complete 160-ETF data source.
CANDIDATES = """
XLK XLV XLF XLE XLI XLP XLU XLB XLY SPY IWM EFA EEM TLT IEF GLD LQD VNQ TIP HYG
VOO IVV VTI VTV VUG VB VO VBK VBR VEA VWO VXUS VT VIG VYM VGT VHT VFH VDE VIS VDC VPU VAW VCR
QQQ QQQM DIA MDY IJR IJH IJS IUSG IUSV IWF IWD IWB IWR IWP IWN IWO IWM
SCHB SCHX SCHG SCHV SCHD SCHA SCHF SCHE SCHH SCHZ SCHR
ITOT IUSV IUSG IJR IJS IYW IYH IYF IYE IYJ IYK IYM IYC IYR IYZ
XBI XHB XRT XOP XME XES XSD XSW XAR XTN XPH KRE KBE KIE
RSP SPLG SPYG SPYV SPHD SPHQ SPHB SPHY SPYD SPYB
BND BNDX BSV BIV BLV VGSH VGIT VGLT VCIT VCSH VCLT VTEB MUB SHY SHV SHYG JNK EMB AGG BIL SGOV
USMV QUAL MTUM VLUE SIZE DGRO HDV DVY NOBL SDY SLYV SLYG IQLT
EWJ EWG EWU EWC EWA EWH EWS EWT EWI EWP EWL EWD EWN EWO EWY EWM EIDO INDA EZA FXI MCHI
GDX GDXJ SLV IAU IAUF PDBC DBC USO UNG
ARKK ARKW ARKG ARKF ARKQ
""".split()
CANDIDATES = list(dict.fromkeys(CANDIDATES))


def score(picks, mu, cov, k, lam=1.0):
    ids = np.asarray(picks, dtype=int)
    return float(mu[ids].mean() - lam * cov[np.ix_(ids, ids)].sum() / (k * k))


def greedy(mu, cov, k):
    n = len(mu)
    selected = []
    for _ in range(k):
        selected.append(max((i for i in range(n) if i not in selected),
                            key=lambda i: score(selected + [i], mu, cov, k)))
    return tuple(sorted(selected))


def one_swap(mu, cov, start, k):
    chosen = tuple(sorted(start))
    best = score(chosen, mu, cov, k)
    steps = 0
    while True:
        winner = chosen
        members = set(chosen)
        available = [i for i in range(len(mu)) if i not in members]
        for drop in chosen:
            for add in available:
                trial = tuple(sorted(members - {drop} | {add}))
                val = score(trial, mu, cov, k)
                if val > best + 1e-12:
                    best = val
                    winner = trial
        if winner == chosen:
            break
        chosen = winner
        steps += 1
    return chosen, best, steps


def main():
    print("Requesting historical market data:", SOURCE, flush=True)
    prices = pd.read_csv(SOURCE, index_col="Date", parse_dates=True).sort_index()
    print("Dataset columns (excluding Date):", len(prices.columns), flush=True)
    print("Candidate ETF tickers:", len(CANDIDATES), flush=True)
    available = [t for t in CANDIDATES if t in prices.columns]
    missing = [t for t in CANDIDATES if t not in prices.columns]
    print("ETF candidates present in file:", len(available), flush=True)
    print("Absent tickers:", ", ".join(missing[:80]), flush=True)

    # Same end-of-2024 information cutoff for all assets; no January 2025 leakage.
    monthly = prices.loc["2020-01-01":"2024-12-31", available].resample("ME").last()
    # Require complete prices for 2022-2024, with the 2020-2021 period
    # available for simple lagged-returns estimation.
    required = monthly.loc["2022-01-31":"2024-12-31"]
    eligible = [t for t in available if len(required) == 36
                and required[t].notna().all() and (required[t] > 0).all()
                and monthly.loc["2021-12-31", t] > 0]
    print("Eligible ETF price series:", len(eligible), flush=True)

    pd.DataFrame({"ticker": CANDIDATES,
                  "in_source": [t in prices.columns for t in CANDIDATES],
                  "eligible": [t in eligible for t in CANDIDATES]}).to_csv(OUT / "ticker_coverage.csv", index=False)

    rows = []
    for n, k in SIZES:
        count = math.comb(n, k)
        feasible = len(eligible) >= n
        rows.append({"etfs": n, "selected": k, "combinations": str(count),
                     "enough_price_series": feasible,
                     "eligible_tickers_found": len(eligible)})
    coverage = pd.DataFrame(rows)
    coverage.to_csv(OUT / "scale_feasibility.csv", index=False)
    print(coverage.to_string(index=False), flush=True)

    # This is a separate classical feasibility exercise: the simple one-month
    # historical mean estimates below are NOT the Random Forest January
    # forecasts used in the existing QAOA study.
    if not eligible:
        print("No eligible prices, cannot benchmark.", flush=True)
        return
    returns = monthly[eligible].pct_change(fill_method=None).loc["2022-01-31":"2024-12-31"]
    mu_all = returns.mean().to_numpy(dtype=float)
    cov_all = returns.cov().to_numpy(dtype=float)
    benchmark = []
    for n, k in SIZES:
        if n > len(eligible):
            print(f"SKIPPED {k}/{n}: insufficient ETF price series", flush=True)
            continue
        mu = mu_all[:n]
        cov = cov_all[:n, :n]
        t0 = time.perf_counter()
        p_g = greedy(mu, cov, k)
        greedy_time = time.perf_counter() - t0
        t1 = time.perf_counter()
        p_swap, swap_score, steps = one_swap(mu, cov, p_g, k)
        swap_time = time.perf_counter() - t1
        record = {"etfs": n, "selected": k,
                  "forecast": "historical monthly mean (preliminary; NOT RF)",
                  "greedy_score": score(p_g, mu, cov, k),
                  "greedy_seconds": greedy_time,
                  "swap_score": swap_score,
                  "swap_seconds": swap_time,
                  "swap_steps": steps,
                  "greedy_portfolio": ", ".join(eligible[i] for i in p_g),
                  "swap_portfolio": ", ".join(eligible[i] for i in p_swap)}
        benchmark.append(record)
        print("CLASSICAL BENCHMARK", record, flush=True)
    pd.DataFrame(benchmark).to_csv(OUT / "classical_benchmarks.csv", index=False)
    print("Data audit complete; NO large-QAOA results claimed.", flush=True)


if __name__ == "__main__":
    main()
