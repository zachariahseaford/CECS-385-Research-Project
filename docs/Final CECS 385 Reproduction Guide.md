# CECS 385 — Final Research Code and Reproduction Guide

## Main research question
Does Qiskit Aer–simulated QAOA select competitive portfolios against conventional algorithms when they optimize the **same forecast return-minus-covariance-risk score**?

**Important:** An exact exhaustive optimum is a mathematical upper bound. QAOA may match it but cannot beat it. It can beat a greedy heuristic only if the greedy heuristic is not already exact.

## Completed core code

| File | Purpose |
|---|---|
| `scripts/final_walkforward_qaoa.py` | Six leakage-controlled historical market dates with exact, greedy, one-swap and QAOA comparisons (36 full trials) |
| `scripts/final_large_prepare.py` | Creates one frozen price/Random Forest/covariance input, exhaustive 3/20 and **exact 6/40**, 25-start classical heuristics for 80 and 160 |
| `scripts/final_large_qaoa.py` | Uses the same frozen input for depth-3 6/40 QAOA and limited 12/80, 24/160 feasibility pilots |
| `scripts/final_results_summary.py` | Creates a Markdown results draft only from actual recorded CSVs; missing results clearly marked |
| `.github/workflows/final-walkforward-qaoa.yml` | Runs smoke check before all six held-out months |
| `.github/workflows/final-large-classical.yml` | Reproducible exact 6/40 and expanded classical score benchmark |
| `.github/workflows/final-large-qaoa.yml` | Single shared frozen source and separate QAOA cases |

## Verified held-out experiment — November 23, 2026

Six target months: **March, June, September and December 2023; March and June 2024**.
At the previous month-end decision date, Random Forest was trained only on historical observations with already-known next-month returns. The risk covariance was calculated from 36 prior return months.

- Total QAOA trials: **36** (two initial states × three seeds × six dates).
- **Greedy equaled exhaustive in every one of the six months**.
- **Five QAOA trials sampled the exhaustive best portfolio**.
- QAOA beat greedy in **zero** trials, because greedy was already exact.
- Original spaced start: **3/18 exact hits**, mean gap **0.006516**.
- Rotated start: **2/18 exact hits**, mean gap **0.003144**.
- Qiskit Aer MPS, depth 3, phase scale 30, 50 COBYLA max evaluations, 128 optimization shots, 1024 final samples.
- All runs were recorded, including misses.
- Evidence: [GitHub Actions run 45265578168](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45265578168).

This confirms that the tuned January 2025 exact-hit rate did **not** generalize unchanged to these separate market dates.

## Verified larger classical experiment

- Real dividend/split-adjusted ETF market data (not synthetic price histories).
- 315 usable Random Forest forecasts after checking complete price histories.
- Exactly **3,838,380 6-of-40 portfolios exhaustively evaluated**, in ~2.32 s for the objective-only vectorized scan.
- Exhaustive 6/40 score: **0.071264604**; exactly matched greedy and 25-start local search.
- Exact 6/40 portfolio: **XLF, XLE, XLU, XLB, VFH, VDE**.
- 12/80 and 24/160 global optima remain **uncertified**. Their 25-start classical scores were ~0.065307 and ~0.062452, respectively.
- Evidence: [GitHub Actions run 45265830611](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45265830611).

## Verified large-circuit feasibility

The latest single-snapshot quantum run used real ETF forecasts and the same scoring objective as its own classical reference.

- 12/80: depth 1, 6 COBYLA evaluations, QAOA score **0.045642**, greedy ~**0.065307**, 128 valid final shots, optimizer not converged.
- 24/160: depth 1, 6 COBYLA evaluations, QAOA score **0.035916**, greedy ~**0.062452**, 128 valid final shots, optimizer not converged.
- These are **feasibility**, not matching-budget quality or speedup trials.
- Depth-3 6/40 has a separate reduced-budget, three-seed job (record status in final results after verification).
- Evidence: [GitHub Actions run 45266001683](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45266001683).

The two independent expanded-data runs used different price-snapshot hashes. Do **not** compare their individual numerical scores across snapshots; each QAOA job should only be compared to its within-workflow reference.

## Run locally

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m pip install yfinance
export PYTHONPATH=scripts

# Full six-month test
python scripts/final_walkforward_qaoa.py --smoke
python scripts/final_walkforward_qaoa.py

# Expanded 20/40/80/160 (this downloads from Yahoo)
python scripts/check_extended_etf_data.py --limit 0 --batch 8
python scripts/final_large_prepare.py
python scripts/final_large_qaoa.py --etfs 40
python scripts/final_large_qaoa.py --etfs 80
python scripts/final_large_qaoa.py --etfs 160

# Build conservative summary from locally available measured CSVs
python scripts/final_results_summary.py
```

**Environment:** The project uses Python 3.11, NumPy/Pandas, scikit-learn, SciPy, Qiskit and Qiskit Aer. For the historical adjusted price retrieval, a working internet connection is required. For the QAOA work, classic simulation runtime rises quickly with qubit count, circuit entanglement and optimization budget.

## Limitations to state explicitly in the final report

1. QAOA uses **classical Qiskit Aer simulation**, not physical quantum hardware; no quantum speedup claim.
2. We optimized a **predicted return-minus-risk score**, not observed future returns; choosing the maximum score is not guaranteed to earn more money.
3. January 2025 served as the QAOA tuning case; six other months were separately tested but only a small sample of market conditions.
4. Greedy was **exact on every verified 20-ETF held-out month and 6/40 case**, meaning it could not be beaten on this objective in these instances.
5. For 12/80 and 24/160, the short QAOA pilots are not matched to a complete, converged classical optimization.
6. The expanded ETF tickers were drawn from a wider source than the original 20 ETFs. Some ETF products overlap heavily, so independence and real-world diversification are not assured.
7. Raw trial CSVs and any cancelled or failed runs must remain in the research record. Do not selectively report only successful seeds.

## Conclusion for presentation

**We did not demonstrate an advantage for QAOA over classical search.** However, we did show (i) that it can sample exact best portfolios, (ii) that cost circuit depth and initial basis state materially change results, (iii) that increasing optimizer evaluation limits alone was not helpful in the tested settings, and (iv) that larger quantum circuits are executable under a limited simulation budget while their optimization quality and runtime remain challenges.


## November 24 update — final exploratory extension

The original no-win result applies only to the original experiments. The additional 72-case screening identified two greedy failures; QAOA matched the exact optimum and beat greedy in two of six conditional trials, both April 2023 at risk penalty 10. It beat neither one-swap local search nor random sampling (which found the optimum in all six trials). No quantum advantage was demonstrated. The separate 30-month classical backtest returned 1.96% for optimized portfolios versus 5.05% equal-weight and 18.96% SPY, gross of costs, with zero-risk-free-rate Sharpe ratios of 0.127, 0.205 and 0.464. Six unit tests passed. Run `python scripts/portfolio_backtest.py` and `python scripts/hard_portfolio_benchmark.py` to reproduce the extension. [Verified results](../results/verified_extension/README.md).
