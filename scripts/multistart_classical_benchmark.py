"""Reproducible multistart classical benchmark for the expanded real-ETF data.

All scenarios reuse one frozen adjusted-price snapshot in a single workflow
run. Starts include the greedy solution and 24 pseudorandom portfolios.
The result is best-known only, not a certified global optimum except 3/20.
"""
import hashlib
import itertools
import math
import time
from pathlib import Path
import numpy as np
import pandas as pd
from large_etf_rf_classical import prepare_forecasts, score, greedy, improve_by_swaps, SCENARIOS

ROOT=Path("results/large_etf_feasibility")
INPUT=ROOT/"new_data_source_monthly_prices.csv"
RANDOM_STARTS=24


def main():
    checksum=hashlib.sha256(INPUT.read_bytes()).hexdigest()
    monthly=pd.read_csv(INPUT,index_col=0,parse_dates=True).sort_index()
    tickers,all_mu,all_cov=prepare_forecasts(monthly)
    print("PRICE_DATA_SHA256",checksum,flush=True)
    print("VALID_FORECASTS",len(tickers),flush=True)
    rows=[]
    for n,k in SCENARIOS:
        if len(tickers)<n:
            print("SKIP insufficient forecasts",k,n,flush=True)
            continue
        mu,cov=all_mu[:n],all_cov[:n,:n]
        rng=np.random.default_rng(385+n)
        initial=greedy(mu,cov,k)
        starts=[initial]+[tuple(sorted(map(int,rng.choice(n,size=k,replace=False))))
                           for _ in range(RANDOM_STARTS)]
        t0=time.perf_counter()
        unique_local={}
        for idx,seeded in enumerate(starts):
            solution,steps=improve_by_swaps(mu,cov,seeded,k)
            val=score(solution,mu,cov,k)
            unique_local[solution]=max(val,unique_local.get(solution,float("-inf")))
            print(f"LOCAL {k}/{n} start {idx} score={val:.9f} swaps={steps}",flush=True)
        elapsed=time.perf_counter()-t0
        winner=max(unique_local,key=unique_local.get)
        gs=score(initial,mu,cov,k)
        row={"etfs":n,"selected":k,"starts":len(starts),
             "data_sha256":checksum,
             "greedy_score":gs,"best_multistart_score":unique_local[winner],
             "improvement_over_greedy":unique_local[winner]-gs,
             "distinct_local_optima":len(unique_local),
             "multistart_seconds":elapsed,
             "best_portfolio":", ".join(tickers[i] for i in winner),
             "exact_optimum_known":False}
        if n==20:
            exact=max(itertools.combinations(range(n),k),key=lambda x:score(x,mu,cov,k))
            row["exact_optimum_known"]=True
            row["exact_score"]=score(exact,mu,cov,k)
            assert row["best_multistart_score"]<=row["exact_score"]+1e-9
        rows.append(row)
        print("BENCHMARK",row,flush=True)
    out=ROOT/"multistart_classical_benchmark.csv"
    pd.DataFrame(rows).to_csv(out,index=False)
    print("COMPLETED",out,flush=True)


if __name__=="__main__":
    main()
