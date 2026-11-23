"""Exploratory risk-aversion sensitivity: can QAOA exceed GREEDY?

This is explicitly post-hoc (NOT the primary lambda=1 experiment).
Predeclare all six held-out dates, risk penalties (10,100), seeds (0,1,2),
and one rotated initial state. All 36 QAOA trials are reported.
Both classical and QAOA maximize the SAME objective for each case.
Exhaustive 3/20 optimum remains the best possible score for each lambda.
"""
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

import final_walkforward_qaoa as f

RISKS=(10.,100.)
SEEDS=(0,1,2)
OUT=Path("results/final_risk_sensitivity")
OUT.mkdir(parents=True,exist_ok=True)


def classical_greedy(mu,cov):
    chosen=[]
    for _ in range(f.K):
        remaining=(i for i in range(len(mu)) if i not in chosen)
        chosen.append(max(remaining,key=lambda i:f.score(chosen+[i],mu,cov)))
    return tuple(sorted(chosen))


def main():
    monthly=f.fetch_prices()
    chosen=tuple(sorted((i+4)%len(f.TICKERS)
                       for i in np.linspace(0,len(f.TICKERS)-1,f.K,dtype=int)))
    rows=[]
    cases=[]
    for target in f.TARGET_MONTHS:
        mu,cov,decision,_=f.forecast_month(monthly,target)
        for lam in RISKS:
            f.RISK_LAMBDA=lam
            exact=max(itertools.combinations(range(len(mu)),f.K),
                      key=lambda picks:f.score(picks,mu,cov))
            exact_score=f.score(exact,mu,cov)
            g=classical_greedy(mu,cov)
            greedy_score=f.score(g,mu,cov)
            best_gap=exact_score-greedy_score
            assert best_gap>=-1e-10
            case={"target_month":target,"decision_date":str(decision.date()),
                  "risk_lambda":lam,"exact_score":exact_score,
                  "exact_portfolio":", ".join(f.TICKERS[i] for i in exact),
                  "greedy_score":greedy_score,
                  "greedy_portfolio":", ".join(f.TICKERS[i] for i in g),
                  "greedy_gap":best_gap,
                  "greedy_is_exact":abs(best_gap)<1e-8}
            cases.append(case)
            pd.DataFrame(cases).to_csv(OUT/"risk_classical_cases.csv",index=False)
            print("EXACT AND GREEDY",json.dumps(case),flush=True)
            for seed in SEEDS:
                trial=f.quantum(mu,cov,chosen,seed)
                gap=exact_score-trial["qaoa_score"]
                if gap< -1e-8:raise RuntimeError("QAOA score exceeded exact optimum")
                row={"risk_lambda":lam,"target_month":target,"seed":seed,
                     "init_method":"rotated","depth":f.DEPTH,
                     "phase_scale":f.SCALE,"optimizer_maxiter":f.MAXITER,
                     "optimizer_shots":f.OPT_SHOTS,"finalshots":f.FINAL_SHOTS,
                     "exact_score":exact_score,"greedy_score":greedy_score,
                     "greedy_is_exact":abs(best_gap)<1e-8,
                     "gap_to_exact":max(gap,0.),
                     "qaoa_beats_greedy":trial["qaoa_score"]>greedy_score+1e-8,
                     "qaoa_matches_exact":abs(gap)<1e-8,**trial}
                rows.append(row)
                pd.DataFrame(rows).to_csv(OUT/"risk_qaoa_trials.csv",index=False)
                print("MEASURED",json.dumps(row),flush=True)
    df=pd.DataFrame(rows)
    summary=df.groupby("risk_lambda",as_index=False).agg(
        trials=("seed","size"),beat_greedy=("qaoa_beats_greedy","sum"),
        exact_hits=("qaoa_matches_exact","sum"),
        mean_gap=("gap_to_exact","mean"),
        mean_seconds=("seconds","mean"))
    summary.to_csv(OUT/"risk_summary.csv",index=False)
    print("RISK SENSITIVITY COMPLETE",len(rows),"trials",flush=True)
    print(summary.to_string(index=False),flush=True)


if __name__=="__main__":
    main()
