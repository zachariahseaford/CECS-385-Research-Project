"""Final CECS 385 out-of-sample QAOA portfolio experiment.

Predeclared six TARGET months (not the January 2025 tuning month):
2023-03, 2023-06, 2023-09, 2023-12, 2024-03, 2024-06.
Each portfolio is selected as of the PREVIOUS month's close. Random Forest
models never train on target-month outcomes. Same ETF data and objective for
QAOA, exhaustive, greedy, and one-swap classical local search.

QAOA methods: spaced and rotated initial states, depth=3, scale=30,
three seeds (0,1,2), COBYLA maxiter=50, optshots=128, finalshots=1024.
All 36 trials are included. No outcome-dependent dates/seeds/stop conditions.

Usage:
  python scripts/final_walkforward_qaoa.py
  python scripts/final_walkforward_qaoa.py --smoke
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.ensemble import RandomForestRegressor
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from large_etf_rf_classical import greedy, improve_by_swaps

SOURCE = "https://raw.githubusercontent.com/manisahni/marketdata/main/daily_adjclose.csv"
TICKERS = ("XLK", "XLV", "XLF", "XLE", "XLI", "XLP", "XLU", "XLB",
           "XLY", "SPY", "IWM", "EFA", "EEM", "TLT", "IEF", "GLD",
           "LQD", "VNQ", "TIP", "HYG")
TARGET_MONTHS = ("2023-03-31","2023-06-30","2023-09-30",
                 "2023-12-31","2024-03-31","2024-06-30")
FEATURES = ("last_month", "last_3_months", "last_6_months", "volatility_3m")
K, RISK_LAMBDA, DEPTH, SCALE = 3, 1., 3, 30.
MAXITER, OPT_SHOTS, FINAL_SHOTS = 50, 128, 1024
SEEDS = (0, 1, 2)
OUT = Path("results/final_walkforward")
OUT.mkdir(parents=True, exist_ok=True)


def fetch_prices():
    raw = pd.read_csv(SOURCE, index_col="Date", parse_dates=True).sort_index()
    missing = [t for t in TICKERS if t not in raw]
    if missing:
        raise ValueError(f"Data source missing required ETFs: {missing}")
    # Do NOT forward fill absent histories; require every price to exist.
    monthly = raw.loc["2018-01-01":"2024-06-30", list(TICKERS)].resample("ME").last()
    if monthly.isna().any().any() or (monthly<=0).any().any():
        raise ValueError("Missing/nonpositive ETF monthly price in required period")
    return monthly


def score(picks,mu,cov,k=K):
    ids=np.asarray(picks,dtype=int)
    return float(mu[ids].sum()/k - RISK_LAMBDA*cov[np.ix_(ids,ids)].sum()/(k*k))


def forecast_month(monthly,target):
    target=pd.Timestamp(target)
    decision=target-pd.offsets.MonthEnd(1)
    if decision not in monthly.index or target not in monthly.index:
        raise ValueError(f"Target/decision month missing: {target} / {decision}")
    ret=monthly.pct_change(fill_method=None)
    mu=[]
    for name in TICKERS:
        p=monthly[name]
        r=ret[name]
        x=pd.DataFrame({"last_month":r,
            "last_3_months":p.pct_change(3),
            "last_6_months":p.pct_change(6),
            "volatility_3m":r.rolling(3).std()})
        y=r.shift(-1)
        # Features from decision are available for predicting target.
        # Train only on rows whose next-month label is already known at decision.
        training=(x.assign(label=y).loc[:decision-pd.offsets.MonthEnd(1)]
                  .dropna(subset=list(FEATURES)+["label"]))
        current=x.loc[[decision],list(FEATURES)]
        if len(training)<24 or current.isna().any().any():
            raise ValueError(f"Insufficient walkforward data for {name} at {decision}")
        reg=RandomForestRegressor(n_estimators=100,min_samples_leaf=3,
                    random_state=7,n_jobs=1)
        reg.fit(training[list(FEATURES)],training["label"])
        mu.append(float(reg.predict(current)[0]))
    history=ret.loc[:decision,list(TICKERS)].tail(36)
    if len(history)!=36 or history.isna().any().any():
        raise ValueError(f"Insufficient covariance history ending {decision}")
    cov=history.cov().to_numpy()
    return np.asarray(mu),cov,decision,ret.loc[target,list(TICKERS)].to_numpy()


def circuit(n,mu,cov,angles,picks):
    a=mu/K-RISK_LAMBDA*np.diag(cov)/(K*K)
    b=np.zeros((n,n))
    for i in range(n):
        for j in range(i+1,n):
            b[i,j]=-2*RISK_LAMBDA*cov[i,j]/(K*K)
    qc=QuantumCircuit(n)
    for idx in picks: qc.x(int(idx))
    for gamma,beta in zip(angles[:DEPTH],angles[DEPTH:]):
        for i in range(n):
            adjustment=a[i]+0.5*sum(b[min(i,j),max(i,j)]
                                      for j in range(n) if j!=i)
            qc.rz(SCALE*gamma*adjustment,i)
        for i in range(n):
            for j in range(i+1,n):
                if abs(b[i,j])>1e-12:
                    qc.rzz(-SCALE*gamma*b[i,j]/2,i,j)
        for offset in (0,1):
            for i in range(offset,n-1,2):
                qc.rxx(beta,i,i+1)
                qc.ryy(beta,i,i+1)
        qc.rxx(beta,n-1,0)
        qc.ryy(beta,n-1,0)
    qc.measure_all()
    return qc


def quantum(mu,cov,start,seed):
    n=len(mu)
    sim=AerSimulator(method="matrix_product_state")
    rng=np.random.default_rng(seed)
    srng=np.random.default_rng(seed+10000)
    calls=0

    def observed(angles,shots):
        compiled=transpile(circuit(n,mu,cov,angles,start),sim,optimization_level=1)
        counts=sim.run(compiled,shots=shots,
            seed_simulator=int(srng.integers(0,2**31-1))).result().get_counts()
        result=[]
        for bits,count in counts.items():
            picks=tuple(i for i,v in enumerate(bits[::-1]) if v=="1")
            if len(picks)==K:
                result.append((picks,count,score(picks,mu,cov)))
        if sum(x[1] for x in result)!=shots:
            raise RuntimeError("XY mixer yielded invalid portfolio cardinality")
        return result

    def loss(angles):
        nonlocal calls
        samples=observed(angles,OPT_SHOTS)
        calls+=1
        return -sum(cnt*s for _,cnt,s in samples)/OPT_SHOTS

    started=time.perf_counter()
    params=rng.uniform(0,2*np.pi,2*DEPTH)
    fit=minimize(loss,params,method="COBYLA",options={"maxiter":MAXITER})
    samples=observed(fit.x,FINAL_SHOTS)
    seconds=time.perf_counter()-started
    best=max(samples,key=lambda x:x[2])
    return {"qaoa_score":best[2],"qaoa_indices":",".join(map(str,best[0])),
        "qaoa_portfolio":", ".join(TICKERS[i] for i in best[0]),
        "optimizer_calls":calls,"optimizer_success":bool(fit.success),
        "seconds":seconds,"valid_shots":sum(x[1] for x in samples)}


def run(smoke=False):
    monthly=fetch_prices()
    months=TARGET_MONTHS[:1] if smoke else TARGET_MONTHS
    seeds=SEEDS[:1] if smoke else SEEDS
    spaced=tuple(map(int,np.linspace(0,len(TICKERS)-1,K,dtype=int)))
    rotated=tuple(sorted((x+4)%len(TICKERS) for x in spaced))
    rows=[]
    checks=[]
    for month in months:
        mu,cov,decision,actual=forecast_month(monthly,month)
        input_hash=hashlib.sha256(
            np.concatenate((mu,cov.ravel())).astype("<f8").tobytes()).hexdigest()
        candidates=list(itertools.combinations(range(len(TICKERS)),K))
        exact=max(candidates,key=lambda c:score(c,mu,cov))
        exact_score=score(exact,mu,cov)
        g=greedy(mu,cov,K)
        gscore=score(g,mu,cov)
        improved,swap_count=improve_by_swaps(mu,cov,g,K)
        sscore=score(improved,mu,cov)
        assert sscore>=gscore-1e-10 and exact_score>=sscore-1e-10
        print("MONTH",month,"decision",decision.date(),
              "EXACT",exact_score,"GREEDY",gscore,"SWAP",sscore,flush=True)
        checks.append({"target_month":month,"decision_date":str(decision.date()),
            "input_sha256":input_hash,"exact_score":exact_score,
            "exact_portfolio":", ".join(TICKERS[i] for i in exact),
            "greedy_score":gscore,"greedy_portfolio":", ".join(TICKERS[i] for i in g),
            "swap_score":sscore,"swap_count":swap_count,
            "greedy_optimal":abs(gscore-exact_score)<1e-8,
            "actual_target_month_available":True})
        pd.DataFrame(checks).to_csv(OUT/("smoke_classical.csv" if smoke else "classical_by_month.csv"),index=False)
        for method,start in (("spaced",spaced),("rotated",rotated)):
            for seed in seeds:
                result=quantum(mu,cov,start,seed)
                gap=exact_score-result["qaoa_score"]
                if gap< -1e-8:
                    raise RuntimeError("QAOA score larger than exhaustive optimum")
                row={"target_month":month,"decision_date":str(decision.date()),
                    "input_sha256":input_hash,"start_method":method,
                    "initial_selection":", ".join(TICKERS[i] for i in start),
                    "seed":seed,"depth":DEPTH,"phase_scale":SCALE,
                    "maxiter":MAXITER,"optimization_shots":OPT_SHOTS,
                    "final_shots":FINAL_SHOTS,"exact_score":exact_score,
                    "greedy_score":gscore,"swap_score":sscore,
                    "gap_to_exact":max(gap,0.),
                    "beat_greedy":result["qaoa_score"]>gscore+1e-8,
                    "beat_swap":result["qaoa_score"]>sscore+1e-8,
                    "exact_hit":abs(gap)<1e-8,**result}
                rows.append(row)
                pd.DataFrame(rows).to_csv(OUT/("smoke_trials.csv" if smoke else "trials.csv"),index=False)
                print("TRIAL",json.dumps(row,default=str),flush=True)
    df=pd.DataFrame(rows)
    summary=df.groupby("start_method",as_index=False).agg(
        trials=("seed","size"),exact_hits=("exact_hit","sum"),
        beat_greedy=("beat_greedy","sum"),mean_gap=("gap_to_exact","mean"),
        best_score=("qaoa_score","max"),mean_runtime_seconds=("seconds","mean"))
    summary.to_csv(OUT/("smoke_summary.csv" if smoke else "summary.csv"),index=False)
    print("WALKFORWARD COMPLETE",len(rows),"QAOA trials",flush=True)
    print(summary.to_string(index=False),flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--smoke",action="store_true")
    run(ap.parse_args().smoke)
