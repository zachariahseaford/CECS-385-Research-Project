"""Predeclared repeat QAOA study; report every result and failure, never stop on scores.

40 ETF: seeds 3-6, depth=2, max 50 COBYLA evaluations, 128/1024 shots.
80/160 ETF: seeds 0-1, depth=2, max 20 evaluations, 64/256 shots.
No exact optimum is known for these large problems. Greedy is a reference only.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from large_etf_rf_classical import prepare_forecasts, greedy, score
from qaoa_larger_real_etfs import run_one, SIZES

OUT=Path("results/large_etf_feasibility")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--etfs",type=int,choices=(40,80,160),required=True)
    ap.add_argument("--seed",type=int,required=True)
    args=ap.parse_args()
    n,k=args.etfs,SIZES[args.etfs]
    if n==40:
        assert args.seed in (3,4,5,6)
        depth,maxiter,optshots,finalshots=2,50,128,1024
    else:
        assert args.seed in (0,1)
        depth,maxiter,optshots,finalshots=2,20,64,256
    monthly=pd.read_csv(OUT/"new_data_source_monthly_prices.csv",index_col=0,parse_dates=True).sort_index()
    names,all_mu,all_cov=prepare_forecasts(monthly)
    assert len(names)>=n, f"Only {len(names)} usable ETF histories; need {n}"
    mu,cov=all_mu[:n],all_cov[:n,:n]
    reference=greedy(mu,cov,k)
    greedy_score=score(reference,mu,cov,k)
    print(f"START PREDECLARED {k}/{n}, seed={args.seed}, depth={depth}, maxiter={maxiter}, optimization shots={optshots}, final shots={finalshots}",flush=True)
    row=run_one(n,k,mu,cov,args.seed,depth,maxiter,optshots,finalshots)
    row.update({"etfs":n,"selected":k,"depth":depth,"maxiter":maxiter,
                "optimization_shots":optshots,"final_shots":finalshots,
                "greedy_score":greedy_score,"difference_from_greedy":row["qaoa_score"]-greedy_score,
                "exact_optimum_known":False,
                "forecast":"January 2025, monthly Random Forest using information through December 2024",
                "study":"prespecified additional seeds, no selective stopping"})
    OUT.mkdir(parents=True,exist_ok=True)
    dest=OUT/f"qaoa_repeat_{n}_seed_{args.seed}.csv"
    pd.DataFrame([row]).to_csv(dest,index=False)
    print("RESULT COMPLETE:",row,flush=True)
    print("CSV SAVED:",dest,flush=True)

if __name__=="__main__":
    main()
