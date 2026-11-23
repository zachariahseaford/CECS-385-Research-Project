"""Test whether raising COBYLA's budget improves 20-ETF simulated QAOA.

Actual original ETF inputs. Fixed QAOA depth=2 and shot counts.
Three predeclared seeds; each seed tested at 50 and 150 evaluations.
Tests optimizer budget, not quantum speedup. Save all outcomes.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from IPython.display import display

NOTEBOOK=Path("data/04 QAOA ETF Scaling Test.ipynb")
OUTPUT=Path("results/qaoa_optimizer_budget")
OUTPUT.mkdir(parents=True,exist_ok=True)

def main():
    notebook=json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    scope={"__name__":"__main__","display":display}
    for idx in (4,5,7,9):
        exec(compile("".join(notebook["cells"][idx]["source"]),f"notebook cell {idx}","exec"),scope)
    problem=scope["make_problem"](20)
    original=scope["QAOA_ITERATIONS"]
    rows=[]
    for budget in (50,150):
        scope["QAOA_ITERATIONS"]=budget
        # run_qaoa reads its globals from the scope used during exec
        for seed in (0,1,2):
            measured=scope["run_qaoa"](problem,seed)
            row={"budget":budget,"seed":seed,
                 "n_etfs":20,"selected":3,"depth":2,
                 "exact_score":problem["exact_score"],
                 "greedy_score":problem["greedy_score"],**measured}
            rows.append(row)
            pd.DataFrame(rows).to_csv(OUTPUT/"optimizer_budget_20.csv",index=False)
            print("BUDGET RESULT",row,flush=True)
    assert original is not None
    df=pd.DataFrame(rows)
    print("SUMMARY",df.groupby("budget").agg(
          trials=("seed","size"),hits=("exact_hit","sum"),
          mean_gap=("gap","mean"),mean_runtime=("runtime_seconds","mean")).to_string(),flush=True)
    print("CONTROLS: same data and seeds; no early stopping on objective score",flush=True)

if __name__=="__main__":
    main()
