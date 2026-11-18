# CECS 385 - Quantum vs Classical ETF Portfolio Selection

For this project, I am comparing quantum computing with classical computing to see how well each method can select ETFs from a historical price dataset. I want to compare which method finds the best portfolio score, how fast it runs, and how much computing time it uses.

I am using 20 ETFs and selecting 3 for each portfolio. This gives 1,140 different combinations.

## How the project works

1. Use historical ETF prices from [marketdata](https://github.com/manisahni/marketdata).
2. Use a Random Forest model to estimate next-month ETF returns.
3. Calculate a portfolio score using predicted return minus a risk penalty.
4. Compare exhaustive search, greedy search, and simulated quantum QAOA using the same score and ETF selections.
5. Check the results against the best score from exhaustive search.

Exhaustive search checks all 1,140 combinations, so it gives the exact best score for the chosen formula. Greedy search selects ETFs one at a time. QAOA uses a quantum circuit simulator (Qiskit Aer) to try to find high-scoring combinations. It does not use a real quantum computer.

**Note:** The portfolio score is not the same as an actual monthly or yearly return. The January 2025 results are one decision period, not evidence of long-term investing performance.

## Project files

- [Main notebook - 20 ETFs](data/03_twenty_etf_exploration.ipynb): current experiment and results.
- [ETF-count scaling experiment](data/04%20QAOA%20ETF%20Scaling%20Test.ipynb): compare QAOA with 6, 10, 15, and 20 ETFs using the same settings. Results are not included until the experiment has been run.
- [QAOA benchmark notebook](data/01_qaoa_benchmark.ipynb): earlier experiments with smaller ETF groups.
- [Classical 100-ETF notebook](data/02_classical_100_etfs.ipynb): separate classical scaling experiment.
- [portfolio.py](scripts/portfolio.py): reusable portfolio scoring and classical optimization code.
- [test_portfolio.py](tests/test_portfolio.py): basic tests for the classical code.
- [Data notes](data/README.md) and [Results notes](results/README.md).

## Running the project

Install the packages in `requirements.txt`, open `data/03_twenty_etf_exploration.ipynb` in Jupyter or Google Colab, and run the cells in order. The notebook downloads its own ETF prices.

For the separate Python tests:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Results so far

These are the saved notebook outputs, not a new run of the code.

| Test | Result |
|---|---|
| January 2025 exhaustive search | 0.044302, XLF / XLE / SPY |
| January 2025 greedy search | 0.044302, XLF / XLE / SPY |
| January 2025 single QAOA quick run | 0.027837, XLF / XLU / LQD |
| July-Dec 2024 greedy vs exhaustive search | Same portfolio in all 6 months |
| QAOA depth 1, 10 runs | Average gap 0.02113; exact best found 0 times |
| QAOA depth 2, 10 runs | Average gap 0.01417; exact best found 0 times |

I still need to compare QAOA across different numbers of ETFs and evaluate longer-term results before making conclusions about yearly returns or risk-adjusted performance. QAOA has not shown an advantage in the current tests.

CECS 385 - University of Tennessee, Knoxville.
