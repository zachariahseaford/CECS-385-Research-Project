# Data

The repository does not ship market price files. Run `python scripts/download_data.py` to fetch the **six-ETF** starter data from [manisahni/marketdata](https://github.com/manisahni/marketdata), or import your own adjusted-close CSV (wide layout, `Date` + ETF tickers).

The 100-ETF notebook can use synthetic demonstration data or a supplied wide CSV of **100 actual funds** with complete histories. Synthetic tickers (`ETF001`, etc.) are not historical funds.

Check licensing and the source's adjustment method. Avoid selecting funds using future survival or data availability without discussing survivorship bias.
