# CECS 385 — Quantum vs. Classical ETF Portfolio Optimization

Research project comparing **classical exhaustive search**, **greedy search**, and **simulated quantum QAOA** when choosing exactly **3 equally weighted ETFs**.

**Main experiment:** [data/03_twenty_etf_exploration.ipynb](data/03_twenty_etf_exploration.ipynb) — 20 ETFs, 1,140 possible three-ETF portfolios, a January 2025 QAOA decision problem, and six historical classical comparisons (July–December 2024).

> This is an educational simulation, **not** an investment recommendation or evidence of quantum speedup. The current main notebook uses **Random Forest return forecasts** as common inputs for the three optimizers. If the forecasting method is changed, all dependent optimization results must be regenerated.

## Research question

How accurately does simulated QAOA approach the exact classical optimum for three-ETF selection, how does it compare with greedy search, and how might performance change as the ETF universe grows?

The question about **increasing ETF counts** remains **future work** for the main 20-ETF QAOA notebook. Do not present its depth-1/depth-2 experiments as an ETF-size experiment.

## Repository layout

| Path | Purpose |
|---|---|
| [data/03_twenty_etf_exploration.ipynb](data/03_twenty_etf_exploration.ipynb) | **Main research notebook**: 20-ETF forecasts, exact search, greedy, QAOA, comparisons and validation |
| [data/01_qaoa_benchmark.ipynb](data/01_qaoa_benchmark.ipynb) | Earlier/supplementary smaller-universe QAOA and backtesting exploration; not the basis of the current presentation numbers |
| [data/02_classical_100_etfs.ipynb](data/02_classical_100_etfs.ipynb) | Supplemental classical scaling exploration, including demonstration-data paths; not a verified real-data 100-ETF QAOA experiment |
| [scripts/portfolio.py](scripts/portfolio.py) | Reusable portfolio score, exhaustive and greedy baselines, and helpers |
| [scripts/download_data.py](scripts/download_data.py) | **Legacy six-ETF** data download helper, separate from the main 20-ETF notebook |
| [tests/test_portfolio.py](tests/test_portfolio.py) | Basic checks of classical portfolio helpers |
| [data/README.md](data/README.md) | Data-source and reproducibility notes |
| [results/README.md](results/README.md) | Where notebook outputs go; notes on which results have been verified |
| [requirements.txt](requirements.txt) | Python package requirements |

Older exploratory notebooks and the six-ETF script are **retained for provenance** and possible scaling tests. They are not required to follow the main notebook.

## How to run the main experiment

1. Use Python/Jupyter (including VS Code/Codespaces or Colab) and install `requirements.txt`. The main notebook also has an installation cell.
2. Open **`data/03_twenty_etf_exploration.ipynb`** (not `notebooks/03_...`).
3. Restart the notebook kernel and run all cells in order. The main notebook fetches adjusted ETF prices from the public [marketdata CSV](https://github.com/manisahni/marketdata) at runtime.
4. Inspect the resulting data checks, classical/greedy comparison, QAOA runs and saved figures. Save the raw trial output before reporting new results.
5. The one-run `QUICK_TEST = True` example is **different** from the repeated 10-trials-per-depth QAOA experiment; report settings separately.

For the reusable classical helper checks:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The legacy six-ETF downloader is **optional** and is not part of the main 20-ETF workflow.

## Core methodology

- **Portfolio rule:** choose exactly 3 of 20 ETFs; weight each selected ETF at 1/3.
- **Score:** estimated monthly portfolio return minus `lambda` times estimated monthly portfolio variance, with **lambda = 1.0** in the main notebook.
- **Inputs:** Random Forest estimates next-month ETF returns from historical features; the risk estimate uses historical monthly-return covariance. The same score and inputs are used by exhaustive, greedy and QAOA.
- **Exact reference:** exhaustive search checks all `C(20,3) = 1140` portfolios and establishes the highest possible score for the *defined mathematical objective*.
- **Greedy:** adds the best next ETF under the scoring rule; not guaranteed to be optimal.
- **QAOA:** Qiskit Aer simulation with a three-selection-preserving XY mixer; final portfolio is the highest-scoring valid sample. Repeated trials compare circuit depths 1 and 2, with 128 shots per optimization evaluation, 1,024 final shots, and a maximum of 50 COBYLA iterations.

## Previously saved main-notebook results

These are historical outputs **embedded in the committed notebook**, not a fresh execution performed by this README:

| Result | Saved value |
|---|---|
| Exact January 2025 benchmark score | 0.044302 (XLF, XLE, SPY) |
| Greedy January 2025 score | 0.044302 (XLF, XLE, SPY) |
| QAOA **one quick-run** score | 0.027837 (XLF, XLU, LQD) |
| Six-month greedy vs exact portfolio matches | 6/6 (July–December 2024) |
| QAOA depth 1: ten trials | Mean gap 0.02113, 0/10 exact hits |
| QAOA depth 2: ten trials | Mean gap 0.01417, 0/10 exact hits |

**Do not** claim the 20 QAOA trials represent 20 different months: the repeated depth comparison uses **one January 2025 problem**. Simulator timings cannot establish a real-hardware speedup.

## Incomplete work / limitations

- Main-notebook QAOA size-growth comparison (e.g. 6, 10, 15 and 20 ETFs) has not yet been established.
- QAOA has not yet been evaluated over the six historical months used for the classical/greedy comparison.
- A meaningful statistical comparison of long-horizon strategy Sharpe ratios and trading-cost sensitivity is not completed in the main notebook.
- Saved notebook outputs should be rechecked from a **fresh restart-and-run-all** before final submission.

## Data and attribution

Public historical ETF adjusted-close data: [manisahni/marketdata](https://github.com/manisahni/marketdata). Confirm date coverage, adjustments and potential survivorship bias. Academic references and claims belong in the report/presentation.

CECS 385 — Transdisciplinary Research, University of Tennessee, Knoxville.
