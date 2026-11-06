"""Download the six-ETF starter dataset from the GitHub marketdata CSV."""
from pathlib import Path
import pandas as pd

URL = 'https://raw.githubusercontent.com/manisahni/marketdata/main/daily_adjclose.csv'
TICKERS = ['XLK', 'XLV', 'XLF', 'XLE', 'XLI', 'XLP']


def main():
    df = pd.read_csv(URL, parse_dates=['Date']).set_index('Date')
    missing = [t for t in TICKERS if t not in df.columns]
    if missing:
        raise ValueError(f'Missing columns: {missing}')
    prices = df.loc['2015-01-01':'2025-12-31', TICKERS].copy()
    if prices.empty or prices.isna().any().any():
        raise ValueError('Missing prices; verify the original CSV and date coverage')
    target = Path(__file__).resolve().parents[1] / 'data' / 'etf_6_adjusted_prices.csv'
    prices.to_csv(target, index_label='Date')
    print('Saved', target, 'with shape', prices.shape)


if __name__ == '__main__':
    main()
