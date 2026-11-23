"""Exploratory fixed-cardinality initial-state experiment for QAOA.

All 21 confirmation trials use ORIGINAL 20-ETF forecast/covariance data, QAOA depth 3,
cost phase-scale 30, 50 COBYLA evaluations, 128 optimization shots,
1024 final shots, and seeds 0/1/2.
Initial states (all 3 assets, no knowledge of the optimum):
  spaced = positions 0,9,19 (original baseline);
  rotated = rotate those positions by 4 indices;
  random = a uniform seeded 3-subset (different each seed).
Every result is archived; no outcome-dependent stopping.
"""
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from IPython.display import display
from qiskit import QuantumCircuit

BOOK=Path("data/04 QAOA ETF Scaling Test.ipynb")
OUT=Path("results/qaoa_initial_state_confirmation")
OUT.mkdir(parents=True,exist_ok=True)
METHODS=("spaced","rotated","random")
SEEDS=(3,4,5,6,7,8,9)
CHOOSE=3

def main():
    nb=json.loads(BOOK.read_text(encoding="utf-8"))
    scope={"__name__":"__main__","display":display}
    for i in (4,5,7,9):
        exec(compile("".join(nb["cells"][i]["source"]),f"notebook cell {i}","exec"),scope)
    problem=scope["make_problem"](20)
    scope["QAOA_DEPTH"]=3
    scope["MIXER_SCALE"]=30.0
    scope["QAOA_ITERATIONS"]=50
    scope["OPTIMIZATION_SHOTS"]=128
    scope["FINAL_SHOTS"]=1024
    digest=hashlib.sha256(np.concatenate([scope["mu"],scope["cov"].ravel()]).astype("<f8").tobytes()).hexdigest()
    # Replace ONLY which computational-basis state gets initialized; all
    # phase gates and mixer gates copied exactly from Notebook 4.
    def qaoa_circuit_with_state(problem, angles):
        n,a,b=problem["n"],problem["a"],problem["b"]
        qc=QuantumCircuit(n)
        picks=scope["INITIAL_PICKS"]
        assert len(picks)==CHOOSE and len(set(picks))==CHOOSE
        for j in picks: qc.x(int(j))
        for gamma,beta in zip(angles[:scope["QAOA_DEPTH"]], angles[scope["QAOA_DEPTH"]:]):
            for j in range(n):
                adjustment=a[j]+0.5*sum(b[min(j,l),max(j,l)] for l in range(n) if l!=j)
                qc.rz(scope["MIXER_SCALE"]*gamma*adjustment,j)
            for j in range(n):
                for l in range(j+1,n):
                    if abs(b[j,l])>1e-12:
                        qc.rzz(-scope["MIXER_SCALE"]*gamma*b[j,l]/2,j,l)
            for offset in (0,1):
                for j in range(offset,n-1,2):
                    qc.rxx(beta,j,j+1)
                    qc.ryy(beta,j,j+1)
            qc.rxx(beta,n-1,0)
            qc.ryy(beta,n-1,0)
        qc.measure_all()
        return qc
    scope["qaoa_circuit"]=qaoa_circuit_with_state
    spaced=tuple(map(int,np.linspace(0,problem["n"]-1,CHOOSE,dtype=int)))
    rows=[]
    for method in METHODS:
        for seed in SEEDS:
            if method=="spaced":
                picks=spaced
            elif method=="rotated":
                picks=tuple(sorted((j+4)%problem["n"] for j in spaced))
            else:
                picks=tuple(sorted(map(int,np.random.default_rng(seed+293).choice(problem["n"],CHOOSE,replace=False))))
            scope["INITIAL_PICKS"]=picks
            measured=scope["run_qaoa"](problem,seed)
            if not np.isfinite(measured["score"]) or measured["valid_shots"]!=1024:
                raise RuntimeError(f"Invalid result for {method} seed {seed}: {measured}")
            row={"init_method":method,"seed":seed,
                 "initial_tickers":", ".join(problem["names"][j] for j in picks),
                 "initial_score":problem["score"](picks),
                 "initial_exact_hit":bool(set(picks)==set(problem["exact"])),
                 "input_sha256":digest,"phase_scale":30,"max_iterations":50,
                 "exact_score":problem["exact_score"],"greedy_score":problem["greedy_score"],
                 **measured}
            rows.append(row)
            pd.DataFrame(rows).to_csv(OUT/"initial_states_trials.csv",index=False)
            print("MEASURED",row,flush=True)
    df=pd.DataFrame(rows)
    summary=df.groupby("init_method",as_index=False).agg(
        trials=("seed","size"),exact_hits=("exact_hit","sum"),
        mean_score=("score","mean"),mean_gap=("gap","mean"),
        best_score=("score","max"),mean_runtime_seconds=("runtime_seconds","mean"))
    summary.to_csv(OUT/"initial_states_summary.csv",index=False)
    print("INITIALIZATION CONFIRMATION COMPLETE",len(rows),"TRIALS",flush=True)
    print(summary.to_string(index=False),flush=True)

if __name__=="__main__":
    main()
