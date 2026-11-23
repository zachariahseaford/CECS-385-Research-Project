"""Final larger-ETF QAOA on ONE frozen shared data and forecast snapshot.

6/40: depth 3, phase scale 30, rotated initialization, 3 seeds,
25 COBYLA max evaluations, 64 optimization and 512 final shots.
12/80, 24/160: resource pilots ONLY, depth 1, 6 evaluations, 32/128 shots.
All cases use same objective/data as frozen exact and classical benchmarks.
Do not claim full-budget QAOA results at 80/160.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from large_etf_rf_classical import score

OUT=Path("results/final_large")
CASE={40:(6,3,25,64,512,(0,1,2)),
      80:(12,1,6,32,128,(0,)),
      160:(24,1,6,32,128,(0,))}
SCALE=30.0


def make_circuit(n,k,mu,cov,angles,depth,starting):
    a=mu/k-np.diag(cov)/(k*k)
    b=-2*cov/(k*k)
    np.fill_diagonal(b,0)
    qc=QuantumCircuit(n)
    for i in starting: qc.x(int(i))
    for gamma,beta in zip(angles[:depth],angles[depth:]):
        for i in range(n):
            qc.rz(SCALE*gamma*(a[i]+b[i].sum()/2),i)
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


def run_one(n,k,mu,cov,seed,depth,maxiter,optshots,finalshots,starting):
    sim=AerSimulator(method="matrix_product_state",n_qubits=n)
    srng=np.random.default_rng(seed+10000)
    rng=np.random.default_rng(seed)
    calls=0
    def sample(angles,shots):
        qc=transpile(make_circuit(n,k,mu,cov,angles,depth,starting),
                     sim,optimization_level=1)
        observed=sim.run(qc,shots=shots,
                         seed_simulator=int(srng.integers(0,2**31-1))).result().get_counts()
        values=[]
        for bitstring,count in observed.items():
            picks=tuple(i for i,b in enumerate(bitstring[::-1]) if b=="1")
            if len(picks)!=k:
                raise RuntimeError(f"Invalid portfolio cardinality {len(picks)} expected {k}")
            values.append((picks,count,score(picks,mu,cov,k)))
        if sum(z[1] for z in values)!=shots:raise RuntimeError("Lost shots")
        return values
    def loss(params):
        nonlocal calls
        vals=sample(params,optshots)
        calls+=1
        return -sum(count*val for _,count,val in vals)/optshots
    started=time.perf_counter()
    angles=rng.uniform(0,2*np.pi,2*depth)
    fit=minimize(loss,angles,method="COBYLA",options={"maxiter":maxiter})
    final=sample(fit.x,finalshots)
    runtime=time.perf_counter()-started
    best=max(final,key=lambda r:r[2])
    return {"seed":seed,"qaoa_score":best[2],
            "qaoa_indices":",".join(map(str,best[0])),
            "runtime_seconds":runtime,"optimizer_calls":calls,
            "optimizer_success":bool(fit.success),"valid_shots":sum(r[1] for r in final)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--etfs",type=int,choices=(40,80,160),required=True)
    n=ap.parse_args().etfs
    k,depth,maxiter,optshots,finalshots,seeds=CASE[n]
    npz=OUT/"frozen_forecasts.npz"
    if not npz.exists(): raise FileNotFoundError(f"Missing frozen input: {npz}")
    frozen=np.load(npz)
    mu=np.asarray(frozen["mu"][:n],dtype=float)
    cov=np.asarray(frozen["cov"][:n,:n],dtype=float)
    tickers=list(frozen["tickers"][:n])
    refs=pd.read_csv(OUT/"classical_benchmarks.csv")
    ref=refs.loc[refs["n"]==n].iloc[0]
    data_hash=(OUT/"source_sha256.txt").read_text().split()[0]
    if data_hash!=ref["price_snapshot_sha256"]:raise RuntimeError("Mismatched data inputs")
    spaced=tuple(map(int,np.linspace(0,n-1,k,dtype=int)))
    starting=tuple(sorted((i+4)%n for i in spaced))
    assert len(starting)==k and len(set(starting))==k
    rows=[]
    for seed in seeds:
        print("START",n,k,"seed",seed,"depth",depth,
              "budget",maxiter,"snapshot",data_hash,flush=True)
        trial=run_one(n,k,mu,cov,seed,depth,maxiter,optshots,finalshots,starting)
        trial.update({"n":n,"k":k,"depth":depth,"phase_scale":SCALE,
             "maxiter":maxiter,"optshots":optshots,"finalshots":finalshots,
             "initial_tickers":", ".join(tickers[i] for i in starting),
             "qaoa_tickers":", ".join(tickers[int(i)] for i in trial["qaoa_indices"].split(",")),
             "greedy_score":float(ref["greedy_score"]),
             "multistart_classical_score":float(ref["best_25_start_score"]),
             "score_minus_greedy":trial["qaoa_score"]-float(ref["greedy_score"]),
             "score_minus_multistart":trial["qaoa_score"]-float(ref["best_25_start_score"]),
             "exact_known":bool(ref["exact_known"]),
             "price_snapshot_sha256":data_hash,
             "experiment_type":"40-ETF reduced-budget depth3" if n==40 else "LARGE CIRCUIT FEASIBILITY ONLY"})
        if n==40:
            trial["exact_score"]=float(ref["exact_score"])
            trial["gap_to_exact"]=float(ref["exact_score"])-trial["qaoa_score"]
            trial["exact_hit"]=abs(trial["gap_to_exact"])<1e-8
            assert trial["gap_to_exact"]>=-1e-8
        rows.append(trial)
        pd.DataFrame(rows).to_csv(OUT/f"qaoa_{n}_trials.csv",index=False)
        print("RESULT",json.dumps(trial),flush=True)
    print("LARGE QAOA COMPLETE",n,len(rows),"recorded trials",flush=True)

if __name__=="__main__":
    main()
