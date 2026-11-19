"""Repeat QAOA for randomly selected ETF groups instead of only nested groups."""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from IPython.display import display

NOTEBOOK = Path("data/04 QAOA ETF Scaling Test.ipynb")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, choices=(10, 15), required=True)
    parser.add_argument("--groups", type=int, default=3)
    parser.add_argument("--seeds", type=int, default=3)
    args = parser.parse_args()
    assert 1 <= args.groups <= 10
    assert 1 <= args.seeds <= 10

    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    scope = {"__name__": "__main__", "display": display}
    for index in (4, 5, 7, 9):
        code = "".join(notebook["cells"][index]["source"])
        exec(compile(code, f"{NOTEBOOK}:cell{index}", "exec"), scope)

    original_tickers = list(scope["TICKERS"])
    original_mu = scope["mu"].copy()
    original_cov = scope["cov"].copy()
    rng = np.random.default_rng(385)
    rows = []
    out = Path("results") / "robustness"
    out.mkdir(parents=True, exist_ok=True)

    for group in range(args.groups):
        indices = rng.permutation(len(original_tickers))
        scope["TICKERS"] = [original_tickers[int(i)] for i in indices]
        scope["mu"] = original_mu[indices]
        scope["cov"] = original_cov[np.ix_(indices, indices)]
        p = scope["make_problem"](args.size)
        assert p["combinations"] == (120 if args.size == 10 else 455)
        assert p["encoding_error"] < 1e-10
        for seed in range(args.seeds):
            result = scope["run_qaoa"](p, seed)
            assert result["valid_shots"] == 1024
            assert np.isfinite(result["score"])
            rows.append({
                "etfs": args.size,
                "group": group,
                "seed": seed,
                "group_tickers": ", ".join(p["names"]),
                "exact_portfolio": ", ".join(p["names"][i] for i in p["exact"]),
                "exact_score": p["exact_score"],
                "greedy_score": p["greedy_score"],
                **result,
            })
            pd.DataFrame(rows).to_csv(out / f"random_groups_{args.size}_trials.csv", index=False)
            print(f"{args.size} ETFs | group {group} | seed {seed} | "
                  f"hit {result['exact_hit']} | gap {result['gap']:.6f} | "
                  f"runtime {result['runtime_seconds']:.2f}s", flush=True)

    df = pd.DataFrame(rows)
    summary = df.groupby(["etfs", "group"], as_index=False).agg(
        runs=("seed", "count"),
        exact_hits=("exact_hit", "sum"),
        mean_gap=("gap", "mean"),
        mean_runtime_seconds=("runtime_seconds", "mean"),
    )
    summary.to_csv(out / f"random_groups_{args.size}_summary.csv", index=False)
    print("VERIFIED GROUP STUDY:", len(df), "trials", flush=True)
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
