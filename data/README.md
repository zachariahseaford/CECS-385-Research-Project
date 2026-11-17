# Data sources and experiment inputs

The **main** experiment is [03_twenty_etf_exploration.ipynb](03_twenty_etf_exploration.ipynb). It downloads adjusted ETF prices directly from the public [manisahni/marketdata](https://github.com/manisahni/marketdata) CSV and analyzes a defined 20-ETF universe. The main notebook's Random Forest forecasts and historical monthly covariance are shared inputs to all three portfolio optimizers.

## Other material in this folder

- [01_qaoa_benchmark.ipynb](01_qaoa_benchmark.ipynb): earlier/supplemental QAOA research; its demo configurations and outputs must not be confused with the main notebook's 20-ETF evidence.
- [02_classical_100_etfs.ipynb](02_classical_100_etfs.ipynb): exploratory classical-scaling notebook; may use synthetic data, which are **not real ETF return evidence**.
- `scripts/download_data.py` outside this folder is a **legacy six-ETF** data downloader. Running it is **not required** for Notebook 3.

Price CSVs are intentionally ignored by Git. The main notebook fetches market data when executed. Before reporting results, verify timestamp alignment, adjusted-price conventions, training/test separation, data coverage and survivorship bias.

**Method note:** Removing or changing Random Forest in the main notebook requires rerunning exhaustive, greedy and QAOA comparisons. Historical outputs in the committed notebook came from the Random Forest-based inputs.
