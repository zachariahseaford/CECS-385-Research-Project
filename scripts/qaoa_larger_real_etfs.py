"""QAOA on real larger ETF problems. Stores measured runs, including optimizer status.

For 40 ETFs we match the depth, trials, iterations and shots of the earlier
scaling experiment. For 80/160 these are only six-iteration FEASIBILITY pilots.
"""
import argparse
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from large_etf_rf_classical import prepare_forecasts, score, greedy

OUTPUT_DIR = Path("results/large_etf_feasibility")
SIZES = {40: 6, 80: 12, 160: 24}


def make_circuit(n, k, mu, cov, angles, depth):
    # Same parameter-to-gate map and XY mixer structure as Notebook 4,
    # generalized to exactly k selected ETFs.
    a = mu/k - np.diag(cov)/(k*k)
    b = -2*cov/(k*k)
    np.fill_diagonal(b, 0)
    circuit = QuantumCircuit(n)
    initial_picks = np.linspace(0, n-1, k, dtype=int)
    for i in initial_picks:
        circuit.x(int(i))
    for gamma, beta in zip(angles[:depth], angles[depth:]):
        for i in range(n):
            circuit.rz(100*gamma*(a[i] + b[i].sum()/2), i)
        for i in range(n):
            for j in range(i+1, n):
                if abs(b[i,j]) > 1e-12:
                    circuit.rzz(-100*gamma*b[i,j]/2, i, j)
        for offset in (0, 1):
            for i in range(offset, n-1, 2):
                circuit.rxx(beta, i, i+1)
                circuit.ryy(beta, i, i+1)
        circuit.rxx(beta, n-1, 0)
        circuit.ryy(beta, n-1, 0)
    circuit.measure_all()
    return circuit


def run_one(n,k,mu,cov,seed,depth,maxiter,optshots,finalshots):
    rng = np.random.default_rng(seed)
    shot_rng = np.random.default_rng(seed + 10000)
    simulator = AerSimulator(method="matrix_product_state", n_qubits=n)
    calls=[0]

    def sample(angles, shots):
        qc = make_circuit(n,k,mu,cov,angles,depth)
        compiled=transpile(qc,simulator,optimization_level=1)
        observed=simulator.run(compiled,shots=shots,
             seed_simulator=int(shot_rng.integers(0,2**31-1))).result().get_counts()
        valid=[]
        for bitstring,count in observed.items():
            picks=tuple(i for i,bit in enumerate(bitstring[::-1]) if bit=="1")
            if len(picks)==k:
                valid.append((picks,count,score(picks,mu,cov,k)))
        return valid

    def loss(angles):
        valid=sample(angles,optshots)
        calls[0]+=1
        total=sum(row[1] for row in valid)
        if not total: return 1e4
        return -sum(row[1]*row[2] for row in valid)/total

    start=time.perf_counter()
    angles=rng.uniform(0,2*np.pi,2*depth)
    fitted=minimize(loss,angles,method="COBYLA",options={"maxiter":maxiter})
    valid=sample(fitted.x,finalshots)
    elapsed=time.perf_counter()-start
    if not valid: raise RuntimeError("No valid QAOA samples")
    picks,count,best=max(valid,key=lambda row:row[2])
    valid_count=sum(row[1] for row in valid)
    assert valid_count==finalshots, (n,valid_count)
    return {"seed":seed, "qaoa_score":best,"runtime_seconds":elapsed,
            "portfolio_indices":", ".join(str(i) for i in picks),
            "optimizer_success":bool(fitted.success),"optimizer_calls":calls[0],
            "valid_final_shots":valid_count}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--etfs",type=int,choices=(40,80,160),required=True)
    args=parser.parse_args()
    n=args.etfs
    k=SIZES[n]
    if n==40:
        depth,maxiter,optshots,finalshots,seeds=2,50,128,1024,range(10)
        label="MATCHED-BUDGET 6/40 study (not matched data source)"
    else:
        depth,maxiter,optshots,finalshots,seeds=1,6,32,128,range(1)
        label="LOW-BUDGET QUANTUM FEASIBILITY PILOT"
    monthly=pd.read_csv(OUTPUT_DIR/"new_data_source_monthly_prices.csv",
                        index_col=0,parse_dates=True).sort_index()
    tickers,full_mu,full_cov=prepare_forecasts(monthly)
    if len(tickers)<n: raise ValueError(f"Only {len(tickers)} valid forecasts; need {n}")
    mu,cov=full_mu[:n],full_cov[:n,:n]
    g=greedy(mu,cov,k)
    gscore=score(g,mu,cov,k)
    rows=[]
    for seed in seeds:
        print("Starting",label,"n",n,"k",k,"seed",seed,flush=True)
        trial=run_one(n,k,mu,cov,seed,depth,maxiter,optshots,finalshots)
        trial.update({"etfs":n,"selected":k,"depth":depth,"maxiter":maxiter,
                      "optshots":optshots,"finalshots":finalshots,
                      "greedy_score":gscore,
                      "difference_from_greedy":trial["qaoa_score"]-gscore,
                      "source":"yfinance auto_adjusted, 2020-2024 RF model",
                      "exact_optimum_known":False})
        rows.append(trial)
        pd.DataFrame(rows).to_csv(OUTPUT_DIR/f"qaoa_{n}_observed_trials.csv",index=False)
        print("MEASURED",trial,flush=True)
    print("COMPLETED REAL-DATA QAOA:",len(rows),"trials",n,"assets",flush=True)


if __name__=="__main__":
    main()
