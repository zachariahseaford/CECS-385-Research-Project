"""CECS 385: predeclared QAOA depth and objective-phase scaling experiment.

Run 27 independent QAOA trials on the *original* January 2025 20-ETF inputs.
Controls: one exact benchmark, same Random Forest forecasts/covariance,
COBYLA max 50, 128 optimization and 1024 final shots, seeds 0/1/2.
Factorial: depth 1/2/3 x phase scale 30/100/300.
Results are complete per trial; never stop because a desirable score appears.
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
DEPTHS=(1,2,3)
SCALES=(30.,100.,300.)
SEEDS=(0,1,2)

def main():
    notebook=json.loads(BOOK.read_text(encoding="utf-8"))
    scope={"__name__":"__main__","display":display}
    for index in (4,5,7,9):
        code="".join(notebook["cells"][index]["source"])
        exec(compile(code,f"{BOOK}:cell{index}","exec"),scope)
    scope["QAOA_ITERATIONS"]=50
    scope["OPTIMIZATION_SHOTS"]=128
    scope["FINAL_SHOTS"]=1024
    problem=scope["make_problem"](20)
    assert problem["encoding_error"]<1e-10
    data_hash=hashlib.sha256(np.concatenate([scope["mu"],scope["cov"].ravel()]).astype("<f8").tobytes()).hexdigest()
    print("FORECAST_COV_SHA256",data_hash,flush=True)
    print("EXACT_SCORE",problem["exact_score"],"EXACT_PORTFOLIO",
          ", ".join(problem["names"][i] for i in problem["exact"]),flush=True)
    rows=[]
    for depth in DEPTHS:
        scope["QAOA_DEPTH"]=depth
        for scale in SCALES:
            scope["MIXER_SCALE"]=scale
            for seed in SEEDS:
                measured=scope["run_qaoa"](problem,seed)
                if not np.isfinite(measured["score"]):
                    raise RuntimeError(f"Nonfinite QAOA score: depth {depth} scale {scale} seed {seed}")
                row={"depth":depth,"phase_scale":scale,"seed":seed,
                     "forecast_cov_sha256":data_hash,"exact_score":problem["exact_score"],
                     "greedy_score":problem["greedy_score"],
                     "optimizer":"COBYLA","max_iterations":50,
                     "optimization_shots":128,"final_shots":1024,
                     **measured}
                rows.append(row)
                pd.DataFrame(rows).to_csv(OUT/"depth_scale_all_trials.csv",index=False)
                print("MEASURED",row,flush=True)
    df=pd.DataFrame(rows)
    summary=df.groupby(["depth","phase_scale"],as_index=False).agg(
        trials=("seed","count"),exact_hits=("exact_hit","sum"),
        mean_score=("score","mean"),mean_gap=("gap","mean"),
        best_score=("score","max"),mean_runtime_seconds=("runtime_seconds","mean"),
        mean_optimizer_calls=("optimizer_calls","mean"))
    summary.to_csv(OUT/"depth_scale_summary.csv",index=False)
    print("EXPERIMENT COMPLETE:",len(df),"TRIALS",flush=True)
    print(summary.to_string(index=False),flush=True)

if __name__=="__main__":
    main()
