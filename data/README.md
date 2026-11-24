# Data and notebooks

The main project is [03_twenty_etf_exploration.ipynb](03_twenty_etf_exploration.ipynb). It uses 20 ETFs from the [marketdata](https://github.com/manisahni/marketdata) adjusted-price dataset. The notebook downloads prices, estimates monthly returns with Random Forest, and runs the three portfolio-selection methods.

Other notebooks:

- [01_qaoa_benchmark.ipynb](01_qaoa_benchmark.ipynb): earlier QAOA tests with smaller ETF groups.
- [02_classical_100_etfs.ipynb](02_classical_100_etfs.ipynb): separate exploratory demonstration supporting DEMO (synthetic generated prices) and CSV modes. **Notebook 02 is excluded from all final-report evidence; its synthetic data and results are not used in the paper.**

Earlier notebooks are retained for reference. Final evidence comes from the real-data Notebook 3, Notebook 4 and the documented real-data scripts/workflows. The submission ZIP preserves downloaded workflow outputs, including the monthly prices, returns and frozen expanded inputs. Raw daily input is documented at https://github.com/manisahni/marketdata/blob/main/daily_adjclose.csv; the exact historical daily snapshot was not archived in the final extension.

Check the data dates before running a new test. The forecasting model should not use future returns when making predictions.
