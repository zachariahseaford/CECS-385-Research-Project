# Results

The main experiment is in [Notebook 3](../data/03_twenty_etf_exploration.ipynb). It contains the saved code outputs and comparisons.

The current results include:

- Exhaustive search, greedy search, and one QAOA quick run for January 2025.
- 10 QAOA runs at depth 1 and 10 at depth 2, all using the same January 2025 decision.
- Six monthly exhaustive-versus-greedy comparisons from July through December 2024.
- Random Forest forecasting checks and QAOA calculation checks.

The graphs and generated CSV files are useful for the report. Some generated files are ignored by `.gitignore`, so they may need to be exported from the notebook after running it.

The [QAOA ETF scaling experiment](QAOA%20ETF%20Scaling%20Results.md) has now completed 40 real-price QAOA trials (10 each for 6, 10, 15 and 20 ETFs). The four GitHub Actions artifact files contain the trial data and graphs. Longer-term QAOA backtesting and actual return/cost comparisons are still unfinished.

The saved notebook output should be checked by restarting and running all cells before the final submission. Results from synthetic test data should not be presented as actual ETF performance.
