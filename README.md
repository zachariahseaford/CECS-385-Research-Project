# CECS 385 — Quantum ETF Portfolio Optimization

A college research project comparing **QAOA**, **exhaustive search**, and a **greedy heuristic** for selecting exactly **3 ETFs**. Random Forest forecasts can provide the *same* return estimates to each optimizer, so optimizer quality is compared fairly.

> **Project status:** Research code and demonstration workflows. Not an investment strategy, a verified quantum advantage, or evidence that any algorithm predicts future prices. Quantum components require a successful run and validation in Colab.

## Research question

**How often does simulated QAOA find the exact optimal three-ETF portfolio, and how do its solution quality, feasibility, and runtime change as the number of ETFs increases?**

The full classical optimizer supplies the *answer key* under the defined score. A higher realized one-month return does **not** mean a portfolio had a better optimization score or that quantum computing predicted the market.

## Files

```text
notebooks/
  01_qaoa_benchmark.ipynb        # AI forecasts, exact/greedy/QAOA small experiments
  02_classical_100_etfs.ipynb    # exact/greedy choose 3 of up to 100
  03_twenty_etf_exploration.ipynb # optional larger quantum illustration
scripts/
  portfolio.py                   # reusable classical methods
  download_data.py               # six ETF starter price download
tests/
  test_portfolio.py              # basic automated checks
data/README.md                   # dataset instructions
results/README.md                # result instructions
docs/methodology.md              # research assumptions and limits
requirements.txt
```

## Quick start — Google Colab

1. Open [Google Colab](https://colab.research.google.com/) → **Open notebook → GitHub** → paste this repository URL after uploading.
2. Open `notebooks/01_qaoa_benchmark.ipynb`.
3. Run its install/import cells. Use `DATA_MODE = "DEMO"` first to verify operation, then `DATA_MODE = "REAL"` for research.
4. Begin with the small QAOA cases. Full QAOA optimization can be slow and must be validated before interpreting the output.
5. Download generated results, store them in `results/` if you want to version them (the `.gitignore` ignores them by default).

## Quick start — GitHub Codespaces or local VS Code

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/download_data.py
```

Open notebooks in VS Code with the Python and Jupyter extensions. If you only need classical algorithms, the Qiskit packages are not required.

## Experiments

| Experiment | ETFs | Exactly selected | Methods | Comments |
|---|---:|---:|---|---|
| Main optimization benchmark | 6, 8 (optionally 10, 12) | 3 | Exact, greedy, QAOA | QAOA simulations to be verified |
| Classical scaling | 10, 25, 50, 75, 100 | 3 | Exact, greedy | At 100: 161,700 candidate portfolios |
| Optional 20-ETF experiment | 20 | 3 | Exact, greedy, QAOA | Potentially heavy QAOA simulation |

## Data

The included data downloader targets the public adjusted-close CSV at [manisahni/marketdata](https://github.com/manisahni/marketdata) for the six initial funds `XLK`, `XLV`, `XLF`, `XLE`, `XLI`, and `XLP`, over 2015–2025. The 100-ETF experiment needs a separate 100-fund historical price CSV to support real-data conclusions. Check license, data coverage, date alignment and potential survivorship bias.

## Scoring

For an equal-weight portfolio of three ETFs:

```
score = predicted_annual_return - risk_lambda * predicted_annual_variance
```

`risk_lambda = 1.0` is the initial risk-aversion assumption. Each optimizer receives the exact same inputs and restrictions.

## How to interpret results

**Primary:** optimal hit rate, difference from exact score, feasibility and runtime by asset-universe size. **Secondary:** walk-forward net returns and Sharpe ratios using the same historical test dates and transaction-cost assumptions. Classical exhaustive search must win or tie on the *defined optimization score*, but not necessarily on realized future returns.

No performance results in this repository should be presented as proof of a quantum speedup. A 100-qubit statevector QAOA experiment is not included.

## Source credit

Price data source: [manisahni/marketdata](https://github.com/manisahni/marketdata). Research background and citations are in the presentation and should be supplemented by primary QAOA portfolio-optimization studies.

## Course

CECS 385 — Transdisciplinary Research, University of Tennessee, Knoxville.
