"""Exploratory historical benchmark; no claims of quantum speedup."""
import itertools
import hashlib
import math
import time
from pathlib import Path
import numpy as np
import pandas as pd
import final_walkforward_qaoa as q

OUT = Path("results/final_extension")
# Fixed calendar and risk grid, excluding original tuning/validation months.
MONTHS = tuple(str(d.date()) for d in pd.date_range("2022-01-31","2024-05-31",freq="ME")
               if str(d.date()) not in q.TARGET_MONTHS)
RISKS = (1., 10., 100.)
SEEDS = (0, 1, 2)
TOL = 1e-8

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    monthly = q.fetch_prices()
    monthly.to_csv(OUT/"monthly_prices.csv")
    candidates = np.asarray(list(itertools.combinations(range(len(q.TICKERS)), q.K)))
    lookup = {tuple(c):i for i,c in enumerate(candidates)}
    screening, trials = [], []
    for month in MONTHS:
        mu,cov,decision,actual = q.forecast_month(monthly,month)
        for risk in RISKS:
            q.RISK_LAMBDA = risk
            # Same objective for all methods, including partial greedy portfolios.
            scores = mu[candidates].sum(axis=1)/q.K - risk*cov[candidates[:,:,None],candidates[:,None,:]].sum(axis=(1,2))/q.K**2
            exact = tuple(candidates[np.argmax(scores)])
            chosen = []
            for _ in range(q.K):
                chosen.append(max((i for i in range(len(mu)) if i not in chosen),
                                  key=lambda i:q.score(chosen+[i],mu,cov)))
            greedy = tuple(sorted(chosen))
            local = greedy
            while True:
                neighbors = [tuple(sorted((set(local)-{a})|{b})) for a in local
                             for b in range(len(mu)) if b not in local]
                best = max(neighbors,key=lambda c:scores[lookup[c]])
                if scores[lookup[best]] <= scores[lookup[local]]+1e-12: break
                local = best
            e,g,l = (float(scores[lookup[c]]) for c in (exact,greedy,local))
            assert e>=l-TOL and l>=g-TOL
            row = dict(month=month,decision=str(decision.date()),risk=risk,
                       input_sha256=hashlib.sha256(np.concatenate((mu,cov.ravel())).astype("<f8").tobytes()).hexdigest(),
                       exact_score=e,greedy_score=g,local_score=l,greedy_gap=e-g,
                       exact_return=float(actual[list(exact)].mean()),greedy_return=float(actual[list(greedy)].mean()),
                       local_return=float(actual[list(local)].mean()))
            screening.append(row)
            pd.DataFrame(screening).to_csv(OUT/"screening.csv",index=False)
            # Evaluate all hard cases; retain every screening result.
            if e-g<=TOL: continue
            start=tuple(sorted((int(i)+4)%len(mu) for i in np.linspace(0,len(mu)-1,q.K,dtype=int)))
            for seed in SEEDS:
                result=q.quantum(mu,cov,start,seed)
                assert result["qaoa_score"]<=e+TOL
                # Match total quantum shots, not merely final shots. Uniform
                # independent sampling with replacement; objective cached.
                budget=result["optimizer_calls"]*q.OPT_SHOTS+q.FINAL_SHOTS
                rng=np.random.default_rng(seed+50000)
                sampled=rng.integers(0,len(candidates),size=budget)
                best=int(sampled[np.argmax(scores[sampled])])
                picks=tuple(int(i) for i in result["qaoa_indices"].split(","))
                trials.append(dict(**row,seed=seed,**result,random_budget=budget,
                                   random_score=float(scores[best]),random_return=float(actual[candidates[best]].mean()),
                                   qaoa_return=float(actual[list(picks)].mean()),
                                   beat_greedy=result["qaoa_score"]>g+TOL,
                                   beat_local=result["qaoa_score"]>l+TOL,
                                   beat_random=result["qaoa_score"]>scores[best]+TOL,
                                   exact_hit=abs(result["qaoa_score"]-e)<=TOL))
                pd.DataFrame(trials).to_csv(OUT/"qaoa_trials.csv",index=False)
    frame=pd.DataFrame(screening)
    frame["hard"]=frame.greedy_gap>TOL
    frame.groupby("risk").agg(cases=("month","size"),hard_cases=("hard","sum"),mean_greedy_gap=("greedy_gap","mean")).to_csv(OUT/"screen_summary.csv")
    if trials:
        pd.DataFrame(trials).groupby("risk").agg(trials=("seed","size"),wins_greedy=("beat_greedy","sum"),wins_local=("beat_local","sum"),wins_random=("beat_random","sum"),exact_hits=("exact_hit","sum")).to_csv(OUT/"qaoa_summary.csv")
    # Nonconsecutive target months are not a continuous investment backtest.
    # Report descriptive realized returns, not annualized Sharpe or wealth.
    frame.groupby("risk")[["exact_return","greedy_return","local_return"]].agg(["mean","std","count"]).to_csv(OUT/"realized_return_summary.csv")
    print("Screened",len(frame),"cases; hard",int(frame.hard.sum()),"; QAOA trials",len(trials),flush=True)

if __name__=="__main__":
    main()
