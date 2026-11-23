"""Frozen-input expanded ETF benchmarks, including an EXACT 6-of-40 solution.

Data source: real adjusted monthly ETF prices prepared by
scripts/check_extended_etf_data.py; no synthetic market histories.
Forecasting methodology matches previous expanded Random Forest experiment.
An exhaustive 6/40 score is evaluated in vectorized batches (3,838,380
combinations); 12/80 and 24/160 report best-known multistart scores only.
"""
import hashlib
import itertools
import json
import math
import time
from pathlib import Path
import numpy as np
import pandas as pd
from large_etf_rf_classical import prepare_forecasts, score, greedy, improve_by_swaps

DATA=Path("results/large_etf_feasibility/new_data_source_monthly_prices.csv")
OUT=Path("results/final_large")
OUT.mkdir(parents=True,exist_ok=True)
CASES=((20,3),(40,6),(80,12),(160,24))

def exact_chunks(mu,cov,k,chunk_size=5000):
    """Exhaustive classical exact maximum, evaluated in bounded-memory batches."""
    n=len(mu)
    t0=time.perf_counter()
    best=float("-inf")
    picks=None
    block=[]
    seen=0
    def evaluate(chunk):
        arr=np.asarray(chunk,dtype=np.int32)
        vals=mu[arr].sum(axis=1)/k-cov[arr[:,:,None],arr[:,None,:]].sum(axis=(1,2))/(k*k)
        arg=int(np.argmax(vals))
        return tuple(map(int,arr[arg])),float(vals[arg])
    for c in itertools.combinations(range(n),k):
        block.append(c)
        if len(block)==chunk_size:
            candidate,val=evaluate(block)
            if val>best: picks,best=candidate,val
            seen+=len(block)
            block.clear()
    if block:
        candidate,val=evaluate(block)
        if val>best: picks,best=candidate,val
        seen+=len(block)
    assert seen==math.comb(n,k)
    return picks,best,time.perf_counter()-t0,seen

def main():
    if not DATA.exists():
        raise FileNotFoundError("Real ETF snapshot missing; run check_extended_etf_data.py first")
    monthly=pd.read_csv(DATA,index_col=0,parse_dates=True).sort_index()
    names,all_mu,all_cov=prepare_forecasts(monthly)
    if len(names)<160:
        raise ValueError(f"Need 160 valid ETF forecasts; found {len(names)}")
    h=hashlib.sha256(DATA.read_bytes()).hexdigest()
    print("RAW_ADJUSTED_PRICE_SHA256",h,"ELIGIBLE",len(names),flush=True)
    np.savez_compressed(OUT/"frozen_forecasts.npz",
       mu=all_mu,cov=all_cov,tickers=np.asarray(names))
    (OUT/"source_sha256.txt").write_text(h+"  new_data_source_monthly_prices.csv\n")
    benchmarks=[]
    for n,k in CASES:
        mu,cov=all_mu[:n],all_cov[:n,:n]
        rng=np.random.default_rng(385+n)
        g=greedy(mu,cov,k)
        gscore=score(g,mu,cov,k)
        states=[g]+[tuple(sorted(map(int,rng.choice(n,size=k,replace=False))))
                    for _ in range(24)]
        t0=time.perf_counter()
        solutions=[]
        for st in states:
            improved,steps=improve_by_swaps(mu,cov,st,k)
            solutions.append((score(improved,mu,cov,k),improved))
        local_secs=time.perf_counter()-t0
        best_local,local_picks=max(solutions)
        row={"n":n,"k":k,"combinations":str(math.comb(n,k)),
             "price_snapshot_sha256":h,"greedy_score":gscore,
             "best_25_start_score":best_local,
             "local_improvement_over_greedy":best_local-gscore,
             "local_25_starts_seconds":local_secs,
             "local_best_tickers":", ".join(names[i] for i in local_picks),
             "exact_known":False}
        if n<=40:
            exact,exscore,exsecs,examined=exact_chunks(mu,cov,k)
            assert exscore>=best_local-1e-9
            row.update({"exact_known":True,"exact_score":exscore,
                        "exact_seconds":exsecs,"exact_portfolio":", ".join(names[i] for i in exact),
                        "greedy_gap":exscore-gscore,"local_gap":exscore-best_local,
                        "exhaustive_evaluated":examined})
        benchmarks.append(row)
        print("CLASSICAL",json.dumps(row),flush=True)
        pd.DataFrame(benchmarks).to_csv(OUT/"classical_benchmarks.csv",index=False)
    print("ALL CLASSICAL BASELINES COMPLETE",len(benchmarks),flush=True)

if __name__=="__main__":
    main()
