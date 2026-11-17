# Data and notebooks

The main project is [03_twenty_etf_exploration.ipynb](03_twenty_etf_exploration.ipynb). It uses 20 ETFs from the [marketdata](https://github.com/manisahni/marketdata) adjusted-price dataset. The notebook downloads prices, estimates monthly returns with Random Forest, and runs the three portfolio-selection methods.

Other notebooks:

- [01_qaoa_benchmark.ipynb](01_qaoa_benchmark.ipynb): earlier QAOA tests with smaller ETF groups.
- [02_classical_100_etfs.ipynb](02_classical_100_etfs.ipynb): separate classical experiment, including possible synthetic demonstration data.

The earlier notebooks are kept for reference, but the presentation's 20-ETF results come from Notebook 3.

Check the data dates before running a new test. The forecasting model should not use future returns when making predictions.
