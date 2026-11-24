"""Continuous monthly classical out-of-sample backtest, gross of trading costs."""
import itertools
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import final_walkforward_qaoa as q

OUT=Path("results/final_extension")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    monthly=q.fetch_prices()
    q.RISK_LAMBDA=1.
    rows=[]
    candidates=list(itertools.combinations(range(len(q.TICKERS)),q.K))
    for target in pd.date_range("2022-01-31","2024-06-30",freq="ME"):
        mu,cov,decision,actual=q.forecast_month(monthly,target)
        exact=max(candidates,key=lambda c:q.score(c,mu,cov))
        greedy=q.greedy(mu,cov,q.K)
        local,_=q.improve_by_swaps(mu,cov,greedy,q.K)
        assert q.score(exact,mu,cov)>=q.score(local,mu,cov)-1e-8
        rows.append(dict(month=target,exact=float(actual[list(exact)].mean()),
                         greedy=float(actual[list(greedy)].mean()),
                         local=float(actual[list(local)].mean()),
                         equal_weight=float(actual.mean()),SPY=float(actual[q.TICKERS.index("SPY")])))
    returns=pd.DataFrame(rows).set_index("month")
    returns.to_csv(OUT/"monthly_realized_returns.csv")
    wealth=(1+returns).cumprod()
    wealth.to_csv(OUT/"classical_wealth.csv")
    summary=pd.DataFrame({"total_return":wealth.iloc[-1]-1,
                          "annualized_volatility":returns.std()*np.sqrt(12),
                          "annualized_sharpe_rf_zero":returns.mean()/returns.std().replace(0,np.nan)*np.sqrt(12)})
    summary.to_csv(OUT/"classical_backtest_summary.csv")
    ax=wealth.plot(title="Classical ETF selection: gross realized wealth (initial $1)",ylabel="Wealth ($)")
    ax.figure.tight_layout()
    ax.figure.savefig(OUT/"classical_backtest.png",dpi=160)
    plt.close(ax.figure)
    print(summary.to_string(),flush=True)

if __name__=="__main__":
    main()
