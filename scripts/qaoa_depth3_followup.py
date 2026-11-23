"""Exploratory follow-up after 27-trial depth-and-phase experiment.

Compare depth 3, phase scale 30, COBYLA maximum 50 vs 120 evaluations
with original 20-ETF January inputs and fixed seeds 0,1,2.
This is post-hoc and should be reported separately from primary factorial.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from IPython.display import display

BOOK=Path("data/04 QAOA ETF Scaling Test.ipynb")
OUT=Path("results/qaoa_depth_scale")
OUT.mkdir(parents=True,exist_ok=True)

def main():
    nb=json.loads(BOOK.read_text(encoding="utf-8"))
    scope={"__name__":"__main__","display":display}
    for i in (4,5,7,9):
        exec(compile("".join(nb["cells"][i]["source"]),f"cell{i}","exec"),scope)
    p=scope["make_problem"](20)
    scope["QAOA_DEPTH"]=3
    scope["MIXER_SCALE"]=30.0
    scope["OPTIMIZATION_SHOTS"]=128
    scope["FINAL_SHOTS"]=1024
    data_hash=hashlib.sha256(np.concatenate([scope["mu"],scope["cov"].ravel()]).astype("<f8").tobytes()).hexdigest()
    rows=[]
    for budget in (50,120):
        scope["QAOA_ITERATIONS"]=budget
        for seed in (0,1,2):
            x=scope["run_qaoa"](p,seed)
            row={"seed":seed,"maxiter":budget,"depth":3,"phase_scale":30,
                 "data_hash":data_hash,"exact_score":p["exact_score"],**x}
            rows.append(row)
            pd.DataFrame(rows).to_csv(OUT/"depth3_iteration_followup.csv",index=False)
            print("FOLLOWUP_RESULT",row,flush=True)
    df=pd.DataFrame(rows)
    summary=df.groupby("maxiter").agg(trials=("seed","size"),hits=("exact_hit","sum"),
            mean_gap=("gap","mean"),best_score=("score","max"),
            mean_runtime=("runtime_seconds","mean"),mean_calls=("optimizer_calls","mean"))
    print("EXPLORATORY SUMMARY",summary.to_string(),flush=True)

if __name__=="__main__":
    main()
