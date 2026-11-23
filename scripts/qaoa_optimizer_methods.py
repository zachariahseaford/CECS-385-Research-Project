"""Controlled QAOA optimizer comparison on original 20-ETF data.

Compare COBYLA with Powell using the SAME three prespecified seeds,
depth, shots, and exact classical optimum. Different optimizers can use
different numbers of circuit evaluations; we report those actual calls.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from IPython.display import display
from scipy.optimize import minimize as scipy_minimize

BOOK=Path("data/04 QAOA ETF Scaling Test.ipynb")
OUT=Path("results/qaoa_optimizer_budget")
OUT.mkdir(parents=True,exist_ok=True)


def main():
    nb=json.loads(BOOK.read_text())
    scope={"__name__":"__main__","display":display}
    for index in (4,5,7,9):
        exec(compile("".join(nb["cells"][index]["source"]),f"cell {index}","exec"),scope)
    problem=scope["make_problem"](20)
    scope["QAOA_ITERATIONS"]=50

    rows=[]
    for optimizer in ("COBYLA","Powell"):
        if optimizer=="Powell":
            def optimize_powell(loss, initial, method=None, options=None):
                return scipy_minimize(loss,initial,method="Powell",
                                      options={"maxiter":50,"maxfev":100,
                                               "xtol":0.1,"ftol":0.01})
            scope["minimize"]=optimize_powell
        else:
            scope["minimize"]=scipy_minimize

        for seed in (0,1,2):
            measured=scope["run_qaoa"](problem,seed)
            row={"optimizer":optimizer,"seed":seed,"etfs":20,"selected":3,
                 "depth":2,"exact_optimum":problem["exact_score"],
                 "known_exact":True,**measured}
            rows.append(row)
            pd.DataFrame(rows).to_csv(OUT/"optimizer_methods_20.csv",index=False)
            print("METHOD RESULT",row,flush=True)
    df=pd.DataFrame(rows)
    print("METHOD SUMMARY",df.groupby("optimizer").agg(
         trials=("seed","size"),exact_hits=("exact_hit","sum"),
         mean_gap=("gap","mean"),mean_calls=("optimizer_calls","mean"),
         mean_seconds=("runtime_seconds","mean")).to_string(),flush=True)

if __name__=="__main__":
    main()
